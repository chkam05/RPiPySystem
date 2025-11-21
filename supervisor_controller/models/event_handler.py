from dataclasses import dataclass
from fnmatch import fnmatchcase
from typing import Any, Callable, Dict, Optional


Action = Callable[[Any, Dict[str, str], Optional[int]], None]


@dataclass(frozen=True)
class EventHandler:

    service_name: Optional[str]
    event: str
    action: Action
    to_state: Optional[str] = None
    result: Optional[int] = None
    priority: int = 0

    def matches(self, event: str, payload: Dict[str, str], extracted_result: Optional[int]) -> bool:
        # 1) event match (globe)
        # Allows: "PROCESS_STATE_*", "SUPERVISOR_STATE_CHANGE", "TICK_*", "*", etc.
        if self.event not in ("*", ""):
            if not fnmatchcase(event, self.event):
                return False
        
         # 2) service match (None => global)
        if self.service_name is not None:
            if payload.get("processname") != self.service_name:
                return False
        
        # 3) to_state match (if provided; only works for events that have to_state in the payload)
        if self.to_state is not None:
            if payload.get("to_state") != self.to_state:
                return False
        
        # 4) result match (if the rule expects a specific result)
        if self.result is not None:
            if extracted_result is None or extracted_result != self.result:
                return False
        
        return True
