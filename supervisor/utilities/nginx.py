from __future__ import annotations
from pathlib import Path
from typing import Optional
import subprocess

from models.rule_result import RuleResult
from utilities.logger import Logger


class NginxUtility:
    def __init__(self, stop_script: Path, logger: Optional[Logger] = None) -> None:
        self.stop_script = stop_script
        self.logger = logger or Logger('event_listener')

    def stop(self) -> RuleResult:
        self.logger.info('Stopping nginx.')

        try:
            result = subprocess.run(
                ['bash', str(self.stop_script), '--no-logo'],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.stdout.strip():
                self.logger.info(result.stdout.strip())
            if result.stderr.strip():
                self.logger.warning(result.stderr.strip())
            if result.returncode == 0:
                return RuleResult.handled('nginx stopped')
            return RuleResult.failed(f'failed to stop nginx, returncode={result.returncode}')
        except FileNotFoundError as ex:
            return RuleResult.failed(f'script not found: {self.stop_script}', ex)
        except subprocess.TimeoutExpired as ex:
            return RuleResult.failed('timeout while running stop_nginx.sh', ex)
        except Exception as ex:
            return RuleResult.failed('exception while running stop_nginx.sh', ex)
