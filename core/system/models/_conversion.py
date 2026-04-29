from __future__ import annotations
from datetime import datetime, timedelta
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


def timedelta_from_seconds(value: Any) -> Optional[timedelta]:
    if value is None or value == '':
        return None
    if isinstance(value, timedelta):
        return value
    if isinstance(value, (int, float)):
        return timedelta(seconds=float(value))

    raise TypeError('Value must be a timedelta, number or None.')


def timedelta_to_seconds(value: Optional[timedelta]) -> Optional[float]:
    if value is None:
        return None

    return value.total_seconds()
