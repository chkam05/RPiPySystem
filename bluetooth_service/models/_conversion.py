from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


def datetime_from_str(value: Any) -> Optional[datetime]:
    if value is None or value == '':
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace('Z', '+00:00'))

    raise TypeError('Value must be a datetime, string or None.')


def datetime_to_str(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None

    return value.isoformat(timespec='seconds')


def bytes_from_list(value: Any) -> bytes | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, list):
        return bytes(int(item) for item in value)

    raise TypeError('Value must be bytes, bytearray, list or None.')


def bytes_to_list(value: bytes | None) -> list[int] | None:
    if value is None:
        return None

    return list(value)
