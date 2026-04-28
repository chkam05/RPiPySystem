from __future__ import annotations
from pathlib import Path
from typing import Iterable, Optional
import os
import shutil
import subprocess
import time

from utilities.logger import Logger
from utilities.nginx import NginxUtility
from models.rule_result import RuleResult


SHUTDOWN_MESSAGE = r"""
  ____  _           _   _   _                   _
 / ___|| |__  _   _| |_| |_(_)_ __   __ _    __| | _____      ___ __
 \___ \| '_ \| | | | __| __| | '_ \ / _` |  / _` |/ _ \ \ /\ / / '_ \
  ___) | | | | |_| | |_| |_| | | | | (_| | | (_| | (_) \ V  V /| | | |  _ _ _
 |____/|_| |_|\__,_|\__|\__|_|_| |_|\__, |  \__,_|\___/ \_/\_/ |_| |_| (_|_|_)
                                    |___/
"""


class SupervisorShutdown:
    def __init__(
        self,
        socket_uri: str,
        supervisorctl_paths: Iterable[Path],
        logger: Optional[Logger] = None,
    ) -> None:
        self.socket_uri = socket_uri
        self.supervisorctl_paths = list(supervisorctl_paths)
        self.logger = logger or Logger('event_listener')

    def _run(self, cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.stdout.strip():
            self.logger.info(result.stdout.strip())
        if result.stderr.strip():
            self.logger.warning(result.stderr.strip())
        return result

    @staticmethod
    def _run_quiet(cmd: list[str], timeout: int = 10) -> bool:
        try:
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
            return result.returncode == 0
        except Exception:
            return False

    def _find_supervisorctl(self) -> str:
        for path in self.supervisorctl_paths:
            if path.exists() and os.access(path, os.X_OK):
                return str(path)
        return shutil.which('supervisorctl') or 'supervisorctl'

    def _supervisorctl(self, *args: str, timeout: int = 15) -> subprocess.CompletedProcess:
        cmd = [self._find_supervisorctl(), '-s', self.socket_uri, *args]
        self.logger.info(f'Running: {" ".join(cmd)}')
        return self._run(cmd, timeout=timeout)

    def _supervisorctl_ok(self, *args: str, timeout: int = 10) -> bool:
        try:
            return self._supervisorctl(*args, timeout=timeout).returncode == 0
        except Exception as ex:
            self.logger.warning(f'supervisorctl failed for args={args}: {ex}')
            return False

    def is_supervisord_running(self) -> bool:
        return self._run_quiet(['pgrep', '-x', 'supervisord'])

    def try_graceful_shutdown(self) -> bool:
        self.logger.info('Attempting graceful shutdown via supervisorctl.')
        if not self._supervisorctl_ok('status'):
            self.logger.warning('supervisorctl is not responding.')
            return False

        if not self._supervisorctl_ok('stop', 'all', timeout=20):
            self.logger.warning('Failed to stop all services via supervisorctl.')

        return self._supervisorctl('shutdown', timeout=15).returncode == 0

    def try_term_supervisord(self) -> bool:
        self.logger.warning('Attempting SIGTERM for supervisord.')
        return self._run_quiet(['pkill', '-TERM', '-x', 'supervisord'])

    def try_kill_supervisord(self) -> bool:
        self.logger.warning('Attempting SIGKILL for supervisord.')
        return self._run_quiet(['pkill', '-KILL', '-x', 'supervisord'])

    def awaits(self, seconds: int) -> bool:
        end = time.time() + max(1, int(seconds))
        while time.time() < end:
            if not self.is_supervisord_running():
                return True
            time.sleep(1)
        return not self.is_supervisord_running()

    def shutdown(self, reason: str, nginx: Optional[NginxUtility] = None) -> RuleResult:
        self.logger.warning(reason)
        self.logger.warning(SHUTDOWN_MESSAGE)

        if nginx:
            nginx_result = nginx.stop()
            if nginx_result.error:
                self.logger.error(nginx_result.message, nginx_result.error)
            elif nginx_result.message:
                self.logger.info(nginx_result.message)

        if not self.is_supervisord_running():
            return RuleResult.handled('no supervisord process found')

        if self.try_graceful_shutdown():
            if self.awaits(5):
                return RuleResult.handled('supervisord has been shut down gracefully')
            self.logger.warning('Graceful shutdown requested, but supervisord is still running.')

        if self.is_supervisord_running():
            if self.try_term_supervisord():
                if self.awaits(3):
                    return RuleResult.handled('supervisord stopped after SIGTERM')
                self.logger.warning('SIGTERM sent, but supervisord is still running.')

        if self.is_supervisord_running():
            if self.try_kill_supervisord():
                if self.awaits(3):
                    return RuleResult.handled('supervisord stopped after SIGKILL')
                self.logger.warning('SIGKILL sent, but supervisord is still running.')

        if self.is_supervisord_running():
            return RuleResult.failed('failed to shutdown supervisord')

        return RuleResult.handled('supervisord has been shut down')
