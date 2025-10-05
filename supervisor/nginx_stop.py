from utils.utils import Utils
from supervisor import childutils
import subprocess
import sys
import traceback

SERVICE_NAME = 'nginx_stop'


def stop_nginx():
    """
    Try to stop the nginx service using systemctl.
    If the process does not have enough privileges, print an error.
    """
    commands = [
        # 1) systemctl (standard way for root)
        ['systemctl', 'stop', 'nginx'],
        # 2) legacy service fallback
        ['/usr/sbin/service', 'nginx', 'stop'],
        ['/sbin/service', 'nginx', 'stop'],
    ]
    
    for cmd in commands:
        try:
            Utils.log(f'Trying to execute: {' '.join(cmd)}', prefix=SERVICE_NAME)
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if r.returncode == 0:
                Utils.log('Nginx service stopped successfully.', prefix=SERVICE_NAME)
                return
            Utils.log(f'Command failed (rc={r.returncode}) stdout=\'{r.stdout.strip()}\' stderr=\'{r.stderr.strip()}\'', prefix=SERVICE_NAME)
        except subprocess.TimeoutExpired as te:
            Utils.log(f'Timeout while executing: {" ".join(cmd)}', prefix=SERVICE_NAME, exc=te)
        except FileNotFoundError:
            Utils.log(f"Command not found: {cmd[0]}", prefix=SERVICE_NAME)
        except Exception as e:
            Utils.log('Exception while stopping nginx', prefix=SERVICE_NAME, exc=e)
            traceback.print_exc(file=sys.stderr)

    Utils.log('Failed to stop nginx. Check permissions or service availability.', prefix=SERVICE_NAME)

def main():
    Utils.log('Listener started. Waiting for events...', prefix=SERVICE_NAME)

    while True:
        try:
            headers, payload = childutils.listener.wait()
            event_name = headers.get('eventname', '')
            Utils.log(f'Event received: {event_name}', prefix=SERVICE_NAME)

            # react to any *_STOPPING variant OR explicit payload marker
            if event_name.startswith('SUPERVISOR_STATE_CHANGE') and (event_name.endswith('_STOPPING') or 'to_state:STOPPING' in payload):
                Utils.log('Supervisor is stopping -> stopping nginx...', prefix=SERVICE_NAME)
                stop_nginx()

            childutils.listener.ok()
        except Exception as e:
            Utils.log('Unexpected exception in listener', prefix=SERVICE_NAME, exc=e)
            childutils.listener.ok()

if __name__ == '__main__':
    main()