from __future__ import annotations
from typing import Any, Dict, Optional
import os
import socket
import subprocess


try:
    import psutil
except ImportError:
    psutil = None


def bytes_to_mb(value: Optional[int]) -> Optional[int]:
    if value is None:
        return None

    return int(value / 1024 / 1024)


def read_first_existing(paths: list[str]) -> Optional[str]:
    for path in paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except OSError:
            continue

    return None


def run_command(args: list[str], timeout: float = 2.0) -> Optional[str]:
    try:
        result = subprocess.run(args, capture_output=True, check=False, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def parse_os_release() -> Dict[str, str]:
    result: Dict[str, str] = {}
    try:
        with open('/etc/os-release', 'r', encoding='utf-8') as f:
            for line in f:
                if '=' not in line:
                    continue
                key, value = line.rstrip().split('=', 1)
                result[key] = value.strip('"')
    except OSError:
        pass

    return result


def hostname() -> Optional[str]:
    try:
        return socket.gethostname()
    except OSError:
        return None


def path_exists(path: str) -> bool:
    try:
        return os.path.exists(path)
    except OSError:
        return False

