import os
import shutil
import subprocess
import sys
import traceback
from typing import Dict, Optional
from supervisor_service.listeners.event_logger import EventLogger
from supervisor_service.listeners.supervisor_shutdown import SupervisorShutdown
from supervisor_service.models.event_handler import EventHandler


SERVICE_NAME = 'event_listener'
SUPERVISOR_SERVICE = 'supervisor_service'
SUPERVISOR_SOCK_URI = 'unix:///tmp/supervisor.sock'

SHUTDOWN_MESSAGE = r"""
  ____  _           _   _   _                   _                             
 / ___|| |__  _   _| |_| |_(_)_ __   __ _    __| | _____      ___ __          
 \___ \| '_ \| | | | __| __| | '_ \ / _` |  / _` |/ _ \ \ /\ / / '_ \         
  ___) | | | | |_| | |_| |_| | | | | (_| | | (_| | (_) \ V  V /| | | |  _ _ _ 
 |____/|_| |_|\__,_|\__|\__|_|_| |_|\__, |  \__,_|\___/ \_/\_/ |_| |_| (_|_|_)
                                    |___/                                     
"""

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
NGINX_STOP_SCRIPT = os.path.join(PROJECT_ROOT, 'scripts', 'stop_nginx.sh')

SUPERVISORCTL_EXEC_PATHS = [
    os.path.join(PROJECT_ROOT, '.venv', 'bin', 'supervisorctl'),
    os.path.join(PROJECT_ROOT, 'venv', 'bin', 'supervisorctl'),
]


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

def action_shutdown_supervisor(service, payload: Dict[str, str], result: Optional[int]) -> None:
    proc = payload.get('processname', '?')
    EventLogger.log(f'{proc} critical termination -> supervisor shutdown.', prefix=SERVICE_NAME)
    EventLogger.log(SHUTDOWN_MESSAGE, prefix=SERVICE_NAME)
    
    try:
        action_stop_nginx(service, payload, result)

        sup_shutdown = SupervisorShutdown(SUPERVISOR_SOCK_URI, SUPERVISORCTL_EXEC_PATHS, SERVICE_NAME)

        # Is Supervisor alive.
        if not sup_shutdown.is_supervisord_running():
            EventLogger.log('No supervisord process found.', prefix=SERVICE_NAME)
            return
        
        # Graceful shutdown via supervisorctl (socket unix).
        if sup_shutdown.try_graceful_shutdown():
            if sup_shutdown.awaits(5):
                EventLogger.log('Supervisord has been shut down (graceful).', prefix=SERVICE_NAME)
                return
            else:
                EventLogger.log('Graceful shutdown requested but supervisord still running.', prefix=SERVICE_NAME)
        
        # SIGTERM.
        if sup_shutdown.is_supervisord_running():
            if sup_shutdown.try_term_supervisord():
                if sup_shutdown.awaits(3):
                    EventLogger.log('Supervisord killed.', prefix=SERVICE_NAME)
                    return
                else:
                    EventLogger.log('SIGKILL sent but supervisord still running.', prefix=SERVICE_NAME)
            else:
                EventLogger.log('Failed to SIGKILL supervisord.', prefix=SERVICE_NAME)
        
        # SIGKILL.
        if sup_shutdown.is_supervisord_running():
            if sup_shutdown.try_kill_supervisord():
                if sup_shutdown.awaits(3):
                    EventLogger.log('Supervisord killed.', prefix=SERVICE_NAME)
                    return
                else:
                    EventLogger.log('SIGKILL sent but supervisord still running.', prefix=SERVICE_NAME)
            else:
                EventLogger.log('Failed to SIGKILL supervisord.', prefix=SERVICE_NAME)
        
        # Final check.
        if sup_shutdown.is_supervisord_running():
            EventLogger.log('Failed to shutdown supervisord.', prefix=SERVICE_NAME)
        else:
            EventLogger.log('Supervisord has been shut down.', prefix=SERVICE_NAME)

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