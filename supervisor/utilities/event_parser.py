from __future__ import annotations
from typing import Any, Dict, Optional

from enums.event_category import EventCategory
from enums.supervisor_event_name import PROCESS_STATE_PREFIX, SUPERVISOR_STATE_CHANGE_PREFIX, SupervisorEventName
from models.supervisor_event import SupervisorEvent


class EventParser:
    @staticmethod
    def to_text(value: Any) -> str:
        return value.decode('utf-8', 'replace') if isinstance(value, (bytes, bytearray)) else str(value or '')

    @classmethod
    def parse_key_value_payload(cls, raw_payload: Any) -> Dict[str, str]:
        text = cls.to_text(raw_payload)
        parts = [part for part in text.split() if ':' in part]
        return dict(part.split(':', 1) for part in parts)

    @staticmethod
    def parse_int(value: Optional[str]) -> Optional[int]:
        if value is None or value == '':
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def parse_bool01(value: Optional[str]) -> Optional[bool]:
        if value is None or value == '':
            return None
        if value == '1':
            return True
        if value == '0':
            return False
        lowered = value.lower()
        if lowered in ('true', 'yes'):
            return True
        if lowered in ('false', 'no'):
            return False
        return None

    @staticmethod
    def category(event_name: str) -> EventCategory:
        if event_name.startswith('PROCESS_COMMUNICATION_'):
            return EventCategory.PROCESS_COMMUNICATION
        if event_name.startswith(PROCESS_STATE_PREFIX):
            return EventCategory.PROCESS
        if event_name.startswith('REMOTE_COMMUNICATION_'):
            return EventCategory.REMOTE_COMMUNICATION
        if event_name.startswith(SUPERVISOR_STATE_CHANGE_PREFIX):
            return EventCategory.SUPERVISOR
        if event_name.startswith('TICK_'):
            return EventCategory.TICK
        return EventCategory.UNKNOWN

    @classmethod
    def parse(cls, headers: Dict[str, Any], raw_payload: Any) -> SupervisorEvent:
        normalized_headers = {str(key): cls.to_text(value) for key, value in (headers or {}).items()}
        event_name = normalized_headers.get('eventname', '')
        payload = cls.parse_key_value_payload(raw_payload)

        if event_name.startswith(SUPERVISOR_STATE_CHANGE_PREFIX) and not payload.get('to_state'):
            payload['to_state'] = event_name.replace(SUPERVISOR_STATE_CHANGE_PREFIX, '', 1)
        if event_name.startswith(PROCESS_STATE_PREFIX) and not payload.get('to_state'):
            payload['to_state'] = event_name.replace(PROCESS_STATE_PREFIX, '', 1)

        return SupervisorEvent(
            event_name=event_name,
            category=cls.category(event_name),
            headers=normalized_headers,
            payload=payload,
            raw_payload=cls.to_text(raw_payload),
            process_name=payload.get('processname'),
            group_name=payload.get('groupname') or payload.get('group'),
            pid=cls.parse_int(payload.get('pid')),
            from_state=payload.get('from_state'),
            to_state=payload.get('to_state'),
            expected_exit=cls.parse_bool01(payload.get('expected')),
            result=cls.parse_int(payload.get('expected')) if event_name == SupervisorEventName.PROCESS_STATE_EXITED.value else None,
        )
