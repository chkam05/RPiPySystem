from __future__ import annotations

import os
from pathlib import Path

from enums.process_state import ProcessState
from enums.supervisor_event_name import SupervisorEventName
from enums.supervisor_state import SupervisorState
from models.event_handler import EventHandler
from models.rule_result import RuleResult
from utilities.logger import Logger
from utilities.nginx import NginxUtility
from utilities.supervisor_shutdown import SupervisorShutdown


SERVICE_NAME = 'event_listener'
CRITICAL_SERVICE_NAMES = [
    'api_service',
    'event_listener'
]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
NGINX_STOP_SCRIPT = PROJECT_ROOT / 'scripts' / 'stop_nginx.sh'
SUPERVISORCTL_EXEC_PATHS = [
    PROJECT_ROOT / '.venv' / 'bin' / 'supervisorctl',
    PROJECT_ROOT / 'venv' / 'bin' / 'supervisorctl',
]


def _logger() -> Logger:
    return Logger(SERVICE_NAME)


def _nginx(logger: Logger) -> NginxUtility:
    return NginxUtility(NGINX_STOP_SCRIPT, logger)


def _supervisor_socket_uri() -> str:
    supervisor_sock = os.getenv('SUPERVISOR_SOCK') or os.getenv('ENV_SUPERVISOR_SOCK')
    if supervisor_sock:
        return f'unix://{supervisor_sock}' if not supervisor_sock.startswith('unix://') else supervisor_sock

    supervisor_url = os.getenv('SUPERVISOR_SOC_URL') or os.getenv('SUPERVISOR_SERVER_URL')
    if supervisor_url:
        return supervisor_url

    return 'unix:///tmp/supervisor.sock'


def _supervisor_shutdown(logger: Logger) -> SupervisorShutdown:
    return SupervisorShutdown(_supervisor_socket_uri(), SUPERVISORCTL_EXEC_PATHS, logger)



def shutdown_on_critical_service_stopping(event) -> RuleResult:
    logger = _logger()
    process = event.process_name or '?'
    return _supervisor_shutdown(logger).shutdown(f'{process} stopping -> supervisor shutdown.', _nginx(logger))


def shutdown_on_critical_service_stopped(event) -> RuleResult:
    logger = _logger()
    process = event.process_name or '?'
    return _supervisor_shutdown(logger).shutdown(f'{process} stopped -> supervisor shutdown.', _nginx(logger))


def shutdown_on_fatal_process(event) -> RuleResult:
    logger = _logger()
    process = event.process_name or '?'
    return _supervisor_shutdown(logger).shutdown(f'{process} fatal state -> supervisor shutdown.', _nginx(logger))


def shutdown_on_unexpected_process_exit(event) -> RuleResult:
    logger = _logger()
    process = event.process_name or '?'
    return _supervisor_shutdown(logger).shutdown(f'{process} unexpected exit -> supervisor shutdown.', _nginx(logger))


def stop_nginx_on_supervisor_stopping(event) -> RuleResult:
    return _nginx(_logger()).stop()


RULE_SHUTDOWN_ON_CRITICAL_SERVICE_STOPPING = EventHandler(
    name='shutdown_on_critical_service_stopping',
    event=SupervisorEventName.PROCESS_STATE_STOPPING.value,
    to_state=ProcessState.STOPPING.value,
    process_name=CRITICAL_SERVICE_NAMES,
    action=shutdown_on_critical_service_stopping,
    priority=100,
)

RULE_SHUTDOWN_ON_CRITICAL_SERVICE_STOPPED = EventHandler(
    name='shutdown_on_critical_service_stopped',
    event=SupervisorEventName.PROCESS_STATE_STOPPED.value,
    to_state=ProcessState.STOPPED.value,
    process_name=CRITICAL_SERVICE_NAMES,
    action=shutdown_on_critical_service_stopped,
    priority=90,
)

RULE_SHUTDOWN_ON_FATAL_PROCESS = EventHandler(
    name='shutdown_on_fatal_process_state',
    event=SupervisorEventName.PROCESS_STATE_FATAL.value,
    to_state=ProcessState.FATAL.value,
    action=shutdown_on_fatal_process,
    priority=80,
)

RULE_SHUTDOWN_ON_UNEXPECTED_EXIT = EventHandler(
    name='shutdown_on_unexpected_process_exit',
    event=SupervisorEventName.PROCESS_STATE_EXITED.value,
    to_state=ProcessState.EXITED.value,
    expected_exit=False,
    action=shutdown_on_unexpected_process_exit,
    priority=70,
)

RULE_STOP_NGINX_ON_SUPERVISOR_STOPPING = EventHandler(
    name='stop_nginx_on_supervisor_stopping',
    event=SupervisorEventName.SUPERVISOR_STATE_CHANGE_STOPPING.value,
    to_state=SupervisorState.STOPPING.value,
    action=stop_nginx_on_supervisor_stopping,
    priority=30,
)


RULES = [
    RULE_SHUTDOWN_ON_CRITICAL_SERVICE_STOPPING,
    RULE_SHUTDOWN_ON_CRITICAL_SERVICE_STOPPED,
    RULE_SHUTDOWN_ON_FATAL_PROCESS,
    RULE_SHUTDOWN_ON_UNEXPECTED_EXIT,
    RULE_STOP_NGINX_ON_SUPERVISOR_STOPPING,
]
