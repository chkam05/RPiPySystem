import sys

from supervisor_controller.rules import RULES, SERVICE_NAME
from supervisor_controller.utils.event_service import SupervisorEventService


if __name__ == '__main__':
    svc = SupervisorEventService(service_name=SERVICE_NAME, rules=RULES)
    sys.exit(svc.run())
