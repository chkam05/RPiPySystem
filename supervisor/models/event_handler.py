from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Union

from models.rule_result import RuleResult
from models.supervisor_event import SupervisorEvent


RuleAction = Callable[[SupervisorEvent], Optional[RuleResult]]
ProcessNameFilter = Union[str, Iterable[str]]


@dataclass(frozen=True)
class EventHandler:
    name: str
    event: str
    action: RuleAction
    process_name: Optional[ProcessNameFilter] = None
    group_name: Optional[ProcessNameFilter] = None
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    expected_exit: Optional[bool] = None
    result: Optional[int] = None
    priority: int = 0
    enabled: bool = True
    run_once: bool = False

    @staticmethod
    def _matches_name_filter(expected: ProcessNameFilter, actual: Optional[str]) -> bool:
        if isinstance(expected, str):
            return actual == expected
        return actual in set(expected)

    def matches(self, event: SupervisorEvent, executed_once: Iterable[str] = ()) -> bool:
        if not self.enabled:
            return False
        if self.run_once and self.name in set(executed_once):
            return False
        if self.event and event.event_name != self.event:
            return False
        if self.process_name is not None and not self._matches_name_filter(self.process_name, event.process_name):
            return False
        if self.group_name is not None and not self._matches_name_filter(self.group_name, event.group_name):
            return False
        if self.from_state is not None and event.from_state != self.from_state:
            return False
        if self.to_state is not None and event.to_state != self.to_state:
            return False
        if self.expected_exit is not None and event.expected_exit != self.expected_exit:
            return False
        if self.result is not None and event.result != self.result:
            return False
        return True
