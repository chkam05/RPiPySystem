from __future__ import annotations
from pathlib import Path
import sys

from models.listener_config import ListenerConfig
from rules import RULES
from utilities.supervisor_listener import SupervisorListener


def main() -> int:
    listener = SupervisorListener(
        rules=RULES,
        config=ListenerConfig(
            service_name='event_listener',
            execute_all_matching_rules=True,
            log_payload=False,
            stop_on_supervisor_stopping=True,
        ),
    )
    return listener.run()


if __name__ == '__main__':
    raise SystemExit(main())
