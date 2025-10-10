import sys
from supervisor_service.listeners.event_service import SupervisorEventService
from supervisor_service.listeners.rules import RULES, SERVICE_NAME


if __name__ == '__main__':
    svc = SupervisorEventService(service_name=SERVICE_NAME, rules=RULES)
    sys.exit(svc.run())
