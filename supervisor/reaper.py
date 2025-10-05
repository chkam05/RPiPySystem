# React when 'supervisor_service' stops: stop all (or shutdown).
from utils.utils import Utils
import sys
import subprocess
from supervisor import childutils

SERVICE_NAME = 'reaper'
TARGET = 'supervisor_service'  # Name of the critical service.
SUPERVISORCTL = '/opt/RPiPySystem/.venv/bin/supervisorctl'
SERVER_URL = 'unix:///tmp/supervisor.sock'  # Must match [supervisorctl] serverurl.

def to_text(s):
    """Ensure bytes -> str decoding for payload parsing."""
    if isinstance(s, bytes):
        return s.decode('utf-8', 'replace')
    return s

def parse_payload(payload) -> dict:
    """Parse key:value pairs from supervisor event payload."""
    text = to_text(payload)
    parts = [p for p in text.split() if ':' in p]
    return dict(p.split(':', 1) for p in parts)

def shutdown_supervisor():
    """Attempt graceful shutdown via supervisorctl."""
    cmd = [SUPERVISORCTL, '-s', SERVER_URL, 'shutdown']

    Utils.log(f'Trying to execute: {' '.join(cmd)}', prefix=SERVICE_NAME)
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        Utils.log(f'Supervisorctl shutdown -> rc={r.returncode}', prefix=SERVICE_NAME)
        if r.stdout.strip():
            Utils.log(f'stdout: {r.stdout.strip()}', prefix=SERVICE_NAME)
        if r.stderr.strip():
            Utils.log(f'stderr: {r.stderr.strip()}', prefix=SERVICE_NAME)
    except FileNotFoundError:
        Utils.log(f'Command not found: {SUPERVISORCTL}', prefix=SERVICE_NAME)
    except Exception as e:
        Utils.log(f'Exception while shutting down supervisor:', prefix=SERVICE_NAME, exc=e)
        traceback.print_exc(file=sys.stdout)
    finally:
        Utils.log(f'Shutdown command execution completed.', prefix=SERVICE_NAME)

def main():
    Utils.log(f'Listener started. Waiting for events...', prefix=SERVICE_NAME)

    while True:
        try:
            headers, payload = childutils.listener.wait()
            event = headers.get('eventname', '')
            data = parse_payload(payload)
            proc = data.get('processname')
            expected = data.get('expected')  # may be None for FATAL

            Utils.log(f'Event received: {event}, process={proc}, expected={expected}', prefix=SERVICE_NAME)

            # React only if TARGET stopped unexpectedly or fatally
            if proc == TARGET and (
                (event == 'PROCESS_STATE_EXITED' and expected == '1') or
                (event == 'PROCESS_STATE_FATAL')
            ):
                Utils.log(f'Detected {TARGET} termination -> initiating supervisor shutdown.', prefix=SERVICE_NAME)
                shutdown_supervisor()
        except Exception as e:
            Utils.log(f'Unexpected exception in listener:', prefix=SERVICE_NAME, exc=e)
            traceback.print_exc(file=sys.stdout)
        finally:
            # Notify supervisor we handled the event
            childutils.listener.ok()

if __name__ == '__main__':
    sys.exit(main())