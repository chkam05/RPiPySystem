import os
import shutil
import subprocess
import time
from typing import List

from .event_logger import EventLogger


class SupervisorShutdown:
    _IS_RUNNING = [
        'pgrep',
        '-x',
        'supervisord'
    ]

    _SIGTERM = [
        'pkill',
        '-TERM',
        '-x',
        'supervisord'
    ]

    _SIGKILL = [
        'pkill',
        '-KILL',
        '-x',
        'supervisord'
    ]

    def __init__(self, socket_uri: str, exec_paths: List[str], service_name: str):
        self.socket_uri: str = socket_uri
        self.exec_paths: List[str] = exec_paths
        self.service_name: str = service_name
    
    def _run(self, cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
        """
        Run the command and return the result, logging stdout/stderr.
        """
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.stdout:
            EventLogger.log(r.stdout.strip(), prefix=self.service_name)
        if r.stderr:
            EventLogger.log(r.stderr.strip(), prefix=self.service_name)
        return r

    @staticmethod
    def _run_quiet(cmd: list[str], timeout: int = 10) -> bool:
        """
        Run command; return True if returncode==0, no error logged.
        """
        try:
            r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
            return r.returncode == 0
        except Exception:
            return False

    def _find_supervisorctl(self) -> str:
        """
        Find supervisorctl in .venv/venv or in PATH.
        """
        for p in self.exec_paths:
            if os.path.exists(p) and os.access(p, os.X_OK):
                return p
        which = shutil.which('supervisorctl')
        return which or 'supervisorctl'

    def _supervisorctl(self, *args: str, timeout: int = 15) -> subprocess.CompletedProcess:
        """
        Call supervisorctl -s unix:///tmp/supervisor.sock <args...>.
        """
        ctl = self._find_supervisorctl()
        cmd = [ctl, '-s', self.socket_uri, *args]
        EventLogger.log(f'Running: {" ".join(cmd)}', prefix=self.service_name)
        return self._run(cmd, timeout=timeout)

    def _supervisorctl_ok(self, *args: str, timeout: int = 10) -> bool:
        """
        Call supervisorctl and return True/False on exit code.
        """
        try:
            r = self._supervisorctl(*args, timeout=timeout)
            return r.returncode == 0
        except Exception:
            return False

    def is_supervisord_running(self) -> bool:
        """
        Check if the 'supervisord' process is alive (pgrep -x supervisord).
        """
        return self._run_quiet(self._IS_RUNNING)

    def try_graceful_shutdown(self) -> bool:
        """
        Try graceful shutdown supervisor via supervisorctl.
        """
        EventLogger.log('Attempting graceful shutdown via supervisorctl ...', prefix=self.service_name)

        # Check if the supervisor responds.
        if not self._supervisorctl_ok('status'):
            EventLogger.log('supervisorctl not responding.', prefix=self.service_name)
            return False

        # Stop all.
        if not self._supervisorctl_ok('stop', 'all'):
            EventLogger.log('Failed to stop services via supervisorctl.', prefix=self.service_name)

        # Shutdown command.
        r = self._supervisorctl('shutdown', timeout=15)
        if r.returncode == 0:
            return True

        EventLogger.log('supervisorctl shutdown failed.', prefix=self.service_name)
        return False
    
    def try_term_supervisord(self) -> bool:
        """
        Try SIGTERM via pkill -TERM -x supervisord.
        """
        EventLogger.log('Attempting to SIGTERM shutdown supervisord ...', prefix=self.service_name)
        return self._run_quiet(self._SIGTERM)

    def try_kill_supervisord(self) -> bool:
        """
        Try SIGKILL supervisord.
        """
        EventLogger.log('Sending SIGKILL (-9) to supervisord ...', prefix=self.service_name)
        return self._run_quiet(self._SIGKILL)

    def awaits(self, seconds: int) -> bool:
        """
        Wait for supervisord to time out, up to N seconds.
        """
        end = time.time() + max(1, int(seconds))
        while time.time() < end:
            if not self.is_supervisord_running():
                return True
            time.sleep(1)
        return not self.is_supervisord_running()