import os
import subprocess
import sys
import traceback
from typing import Dict, Optional
from supervisor_service.listeners.event_logger import EventLogger
from supervisor_service.models.event_handler import EventHandler


SERVICE_NAME = 'event_listener'
SUPERVISOR_SERVICE = 'supervisor_service'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
NGINX_STOP_SCRIPT = os.path.join(PROJECT_ROOT, 'scripts', 'stop_nginx.sh')


# region --- On Supervisor shutdown, stop nginx ---

def action_stop_nginx(service, payload: Dict[str, str], result: Optional[int]) -> None:
    EventLogger.log('Supervisor STOPPING -> stopping nginx...', prefix=SERVICE_NAME)

    try:
        r = subprocess.run(
            ['bash', NGINX_STOP_SCRIPT, '--no-logo'],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        returncode = r.returncode
        stdout = r.stdout.strip()
        stderr = r.stderr.strip()

        if stdout:
            EventLogger.log(stdout, prefix=SERVICE_NAME)
        if stderr:
            EventLogger.log(stderr, prefix=SERVICE_NAME)

        if returncode == 0:
            EventLogger.log('Nginx stopped.', prefix=SERVICE_NAME)
            return
    except FileNotFoundError:
        EventLogger.log(f'Script not found: {NGINX_STOP_SCRIPT}', prefix=SERVICE_NAME)
    except subprocess.TimeoutExpired as te:
        EventLogger.log('Timeout while running nginx_stop.sh', prefix=SERVICE_NAME, exc=te)
    except Exception as e:
        EventLogger.log('Exception while running nginx_stop.sh', prefix=SERVICE_NAME, exc=e)
        traceback.print_exc(file=sys.stderr)

    EventLogger.log('Failed to stop nginx via script.', prefix=SERVICE_NAME)

RULE_SUPERVISOR_STOPPING = EventHandler(
    service_name=None,
    event='SUPERVISOR_STATE_CHANGE_STOPPING',
    to_state='STOPPING',
    action=action_stop_nginx,
    priority=30,
)

# endregion --- On Supervisor shutdown, stop nginx ---

# region --- Process rules (example: critical process terminations) ---

SHUTDOWN_SUPERVISOR_COMMANDS = [
    'supervisorctl',
    'shutdown'
]

def action_shutdown_supervisor(service, payload: Dict[str, str], result: Optional[int]) -> None:
    proc = payload.get('processname', '?')
    EventLogger.log(f'{proc} critical termination -> supervisor shutdown.', prefix=SERVICE_NAME)
    
    try:
        action_stop_nginx(service, payload, result)
        r = subprocess.run(SHUTDOWN_SUPERVISOR_COMMANDS, capture_output=True, text=True, timeout=30)

        returncode = r.returncode
        stdout = r.stdout.strip()
        stderr = r.stderr.strip()

        if stdout:
            EventLogger.log(stdout, prefix=SERVICE_NAME)
        if stderr:
            EventLogger.log(stderr, prefix=SERVICE_NAME)
        if returncode == 0:
            return
    except FileNotFoundError:
        EventLogger.log('Not found: supervisorctl', prefix=SERVICE_NAME)
    except Exception as e:
        EventLogger.log('Exception during supervisor shutdown', prefix=SERVICE_NAME, exc=e)
        traceback.print_exc(file=sys.stderr)

# PROCESS_STATE_STOPPING: Manually stopping supervisor_service -> shutdown
RULE_STOP_SUPERVISOR_ON_RPC = EventHandler(
    service_name=SUPERVISOR_SERVICE,
    event='PROCESS_STATE_STOPPING',
    action=action_shutdown_supervisor,
    priority=100,
)

# PROCESS_STATE_STOPPED: Stopped supervisor_service -> shutdown
RULE_STOPPED_SUPERVISOR_ON_RPC = EventHandler(
    service_name=SUPERVISOR_SERVICE,
    event='PROCESS_STATE_STOPPED',
    action=action_shutdown_supervisor,
    priority=90,
)

# PROCESS_STATE_FATAL: Fatal start (was unable to restart) -> shutdown
RULE_SUPERVISOR_SERVICE_FATAL = EventHandler(
    service_name=None,
    event='PROCESS_STATE_FATAL',
    action=action_shutdown_supervisor,
    priority=80,
)

# PROCESS_STATE_EXITED: Unexpected termination -> shutdown
RULE_SUPERVISOR_SERVICE_UNEXPECTED_EXIT = EventHandler(
    service_name=None,
    event='PROCESS_STATE_EXITED',
    result=1,
    action=action_shutdown_supervisor,
    priority=70,
)

# endregion --- Process rules (example: critical process terminations) ---

RULES = [
    RULE_STOP_SUPERVISOR_ON_RPC,
    RULE_STOPPED_SUPERVISOR_ON_RPC,
    RULE_SUPERVISOR_SERVICE_FATAL,
    RULE_SUPERVISOR_SERVICE_UNEXPECTED_EXIT,
    RULE_SUPERVISOR_STOPPING
]