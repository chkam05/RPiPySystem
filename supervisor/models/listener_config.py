from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ListenerConfig:
    service_name: str = 'event_listener'
    execute_all_matching_rules: bool = True
    log_payload: bool = False
    stop_on_supervisor_stopping: bool = True
    stop_on_signal: bool = True
    max_payload_log_length: int = 500
    supervisor_socket_uri: Optional[str] = None
