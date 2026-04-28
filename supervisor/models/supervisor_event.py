from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional

from enums.event_category import EventCategory
from enums.process_state import ProcessState
from enums.supervisor_event_name import PROCESS_STATE_PREFIX, SUPERVISOR_STATE_CHANGE_PREFIX
from enums.supervisor_state import SupervisorState


@dataclass(frozen=True)
class SupervisorEvent:
    event_name: str
    category: EventCategory
    headers: Dict[str, str]
    payload: Dict[str, str]
    raw_payload: str = ''
    process_name: Optional[str] = None
    group_name: Optional[str] = None
    pid: Optional[int] = None
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    expected_exit: Optional[bool] = None
    result: Optional[int] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def is_process_event(self) -> bool:
        return self.category == EventCategory.PROCESS

    @property
    def is_supervisor_event(self) -> bool:
        return self.category == EventCategory.SUPERVISOR

    @property
    def process_state(self) -> ProcessState:
        if self.category != EventCategory.PROCESS:
            return ProcessState.UNKNOWN
        suffix = self.event_name.replace(PROCESS_STATE_PREFIX, '', 1)
        try:
            return ProcessState(suffix)
        except ValueError:
            return ProcessState.UNKNOWN

    @property
    def supervisor_state(self) -> SupervisorState:
        value = self.to_state or self.event_name.replace(SUPERVISOR_STATE_CHANGE_PREFIX, '', 1)
        try:
            return SupervisorState(value)
        except ValueError:
            return SupervisorState.UNKNOWN

    def payload_value(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.payload.get(key, default)
