import os
import signal
import sys
import threading
import traceback
from typing import ClassVar, Dict, List, Optional
from supervisor import childutils

from supervisor_service.listeners.event_logger import EventLogger
from supervisor_service.models.event_handler import EventHandler


_shutdown_once = threading.Event()


def _sig_shutdown(signame: str, service_obj: 'SupervisorEventService') -> None:
    if _shutdown_once.is_set():
        return
    _shutdown_once.set()
    try:
        EventLogger.log(f'{signame} received -> dispatching STOPPING...', prefix=service_obj.service_name)
        pseudo_event = 'SUPERVISOR_STATE_CHANGE_STOPPING'
        pseudo_payload = {
            'processname': 'supervisord',
            'groupname': 'supervisord',
            'to_state': 'STOPPING',
        }
        service_obj._dispatch(pseudo_event, pseudo_payload)
    except Exception as e:
        EventLogger.log('Exception in signal shutdown handler', prefix=service_obj.service_name, exc=e)
    finally:
        os._exit(0)


class SupervisorEventService:

    PROCESS_STATE_EXITED: ClassVar[str] = 'PROCESS_STATE_EXITED'

    def __init__(self, service_name: str, rules: Optional[List[EventHandler]]):
        self.service_name = service_name
        self.rules: List[EventHandler] = rules if rules else []
        self._stopping = False

        signal.signal(signal.SIGTERM, lambda s, f: _sig_shutdown('SIGTERM', self))
        signal.signal(signal.SIGINT,  lambda s, f: _sig_shutdown('SIGINT',  self))

    # region --- Utilities ---

    @staticmethod
    def _to_text(b) -> str:
        return b.decode('utf-8', 'replace') if isinstance(b, (bytes, bytearray)) else str(b)
    
    def _parse_payload(self, payload_raw) -> Dict[str, str]:
        text = self._to_text(payload_raw)
        parts = [p for p in text.split() if ":" in p]
        return dict(p.split(":", 1) for p in parts)
    
    def _extract_result(self, event: str, payload: Dict[str, str]) -> Optional[int]:
        if event == self.PROCESS_STATE_EXITED:
            val = payload.get('expected')
            try:
                return int(val) if val is not None else None
            except ValueError:
                return None
        return None

    # endregion --- Utilities ---

    # region --- Logging ---

    def _log(self, event: str, p: Dict[str, str]) -> None:
        process_name = p.get('processname', 'supervisord')
        group_name = p.get('groupname', p.get('group', None))
        process_id = p.get('pid', None)
        process_result = p.get('expected', None)
        state_from = p.get('from_state', None)
        state_to = p.get('to_state', None)

        prefix = ''

        prefix += f'{group_name}: ' if (group_name and group_name.strip()) else ''
        prefix += process_name
        prefix += f' ({process_id})' if (process_id and process_id.strip()) else ''

        e = event if (event and event.strip()) else None
        f = state_from if (state_from and state_from.strip()) else None
        t = state_to if (state_to and state_to.strip()) else None

        state_change = (f'{e}: {f} -> {t}'  if e and f and t else
                        f'{f} -> {t}'       if f and t else
                        f'{e} -> {t}'       if e and t else
                        f'{f} -> {e}'       if f and e else
                        f'{e}'              if e else
                        f'{f}'              if f else
                        f'? -> {t}'         if t else
                        None)

        message = f'[{prefix}]'
        message += f' {state_change}' if (state_change and state_change.strip()) else ''
        message += f': {process_result}' if (process_result and process_result.strip()) else ''

        EventLogger.log(message, prefix=self.service_name)

    # endregion --- Logging ---

    # region --- Rule Engine ---

    def _select_rules(self, event: str, payload: Dict[str, str], result: Optional[int]) -> List[EventHandler]:
        # Collect matching rules
        matches = [r for r in self.rules if r.matches(event, payload, result)]

        # Prefer more specific (higher priority) first
        matches.sort(key=lambda r: r.priority, reverse=True)
        return matches

    def _dispatch(self, event: str, payload: Dict[str, str]) -> None:
        # Extract simplified result
        result = self._extract_result(event, payload)

        # Choose matching rules
        rules = self._select_rules(event, payload, result)

        if not rules:
            # Optional: handle wildcard fallback if present in RULES
            fallback = [r for r in self.rules if r.event == "*" and r.matches(event, payload, result)]
            if fallback:
                rules = fallback

        # Execute first matched rule (deterministic). If you prefer "execute all", iterate all.
        if rules:
            rule = rules[0]
            try:
                rule.action(self, payload, result)
            except Exception as e:
                EventLogger.log("Exception in rule action", prefix=self.service_name, exc=e)
                traceback.print_exc(file=sys.stderr)

    # endregion --- Rule Engine ---
    
    def _handle_event(self, headers, payload_raw) -> None:
        event = headers.get('eventname', '')
        payload = self._parse_payload(payload_raw)

        # Normalize to_state for SUPERVISOR_STATE_CHANGE_* if missing in payload
        if event.startswith('SUPERVISOR_STATE_CHANGE') and ('to_state' not in payload or not payload.get('to_state')):
            # event looks like SUPERVISOR_STATE_CHANGE_STOPPING / RUNNING, etc.
            try:
                payload['to_state'] = event.split('_')[-1]
            except Exception:
                pass

        self._log(event, payload)
        self._dispatch(event, payload)

        if event.startswith('SUPERVISOR_STATE_CHANGE') and payload.get('to_state') == 'STOPPING':
            self._stopping = True

    def run(self) -> int:
        EventLogger.log("Listener started. Waiting for events...", prefix=self.service_name)
        while True:
            try:
                headers, payload = childutils.listener.wait()
                self._handle_event(headers, payload)
            except Exception as e:
                EventLogger.log("Unexpected exception in listener", prefix=self.service_name, exc=e)
                traceback.print_exc(file=sys.stderr)
            finally:
                if getattr(self, '_stopping', False):
                    break
                childutils.listener.ok()
        return 0