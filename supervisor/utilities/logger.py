from __future__ import annotations
from datetime import datetime
from typing import Optional
import sys
import traceback


class Logger:
    def __init__(self, prefix: Optional[str] = None) -> None:
        self.prefix = prefix

    def _write(self, level: str, message: str, exc: Optional[Exception] = None) -> None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = f' [{self.prefix}]' if self.prefix else ''
        print(f'[{timestamp}] [{level}]{prefix} {message}', file=sys.stderr, flush=True)
        if exc:
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr, chain=False)

    def debug(self, message: str) -> None:
        self._write('DEBUG', message)

    def info(self, message: str) -> None:
        self._write('INFO', message)

    def warning(self, message: str) -> None:
        self._write('WARN', message)

    def error(self, message: str, exc: Optional[Exception] = None) -> None:
        self._write('ERROR', message, exc)

