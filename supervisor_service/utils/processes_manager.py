import socket
from typing import Any, Dict, List, Tuple
from xmlrpc import client as xmlrpc_client

from supervisor_service.config import EXCLUDED_FROM_STOP_ALL
from supervisor_service.models.process_action import ProcessAction
from supervisor_service.models.process_action_result import ProcessActionResult
from supervisor_service.models.process_details import ProcessDetails
from supervisor_service.models.process_info import ProcessInfo


class ProcessesManager:
    def __init__(self, server_proxy: xmlrpc_client.ServerProxy):
        self._server_proxy = server_proxy
    
    # --- Helper methods ---
    
    def _action_success(self, action: ProcessAction, info: Dict[str, Any]) -> Tuple[bool, str]:
        name = info.get('name')
        statename = (info.get('statename') or '').upper()

        if action == ProcessAction.START or action == ProcessAction.RESTART:
            ok = statename in ('STARTING', 'RUNNING')
            msg = f'{name} state={statename}'
            return ok, msg

        if action == ProcessAction.STOP:
            ok = statename in ('STOPPED', 'EXITED', 'FATAL', 'STOPPING')
            msg = f'{name} state={statename}'
            return ok, msg

        return False, f'{name} unknown state'

    @staticmethod
    def _wrap_call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (ConnectionRefusedError, TimeoutError, socket.gaierror, socket.timeout, OSError) as e:
            raise RuntimeError(f'Supervisor xmlrpc unreachable: {e.__class__.__name__}') from e
        except xmlrpc_client.ProtocolError as e:
            raise RuntimeError(f'Supervisor protocol error: {e.errcode} {e.errmsg}') from e
        except xmlrpc_client.Fault as e:
            raise RuntimeError(f'Supervisor fault: {e.faultCode} {e.faultString}') from e

    # --- API methods ---

    def list_processes(self) -> List[ProcessInfo]:
        data: List[Dict[str, Any]] = self._wrap_call(self._server_proxy.supervisor.getAllProcessInfo)
        return ProcessInfo.list_from_supervisor(data)
    
    def list_processes_public(self) -> List[Dict[str, Any]]:
        return ProcessInfo.list_to_public(self.list_processes())

    def start(self, name: str) -> ProcessActionResult:
        self._wrap_call(self._server_proxy.supervisor.startProcess, name)
        info = self.info(name)
        ok, msg = self._action_success(ProcessAction.START, info)
        return ProcessActionResult(name=name, action=ProcessAction.START, state=ok, message=msg)

    def stop(self, name: str) -> ProcessActionResult:
        self._wrap_call(self._server_proxy.supervisor.stopProcess, name)
        info = self.info(name)
        ok, msg = self._action_success(ProcessAction.STOP, info)
        return ProcessActionResult(name=name, action=ProcessAction.STOP, state=ok, message=msg)

    def restart(self, name: str) -> ProcessActionResult:
        self.stop(name)
        self.start(name)
        info = self.info(name)
        ok, msg = self._action_success(ProcessAction.RESTART, info)
        return ProcessActionResult(name=name, action=ProcessAction.RESTART, state=ok, message=msg)

    def info(self, name: str) -> ProcessDetails:
        raw: Dict[str, Any] = dict(self._wrap_call(self._server_proxy.supervisor.getProcessInfo, name))
        return ProcessDetails.from_supervisor_dict(raw)

    def info_public(self, name: str) -> Dict[str, Any]:
        return self.info(name).to_public()

    def stop_all(self) -> None:
        excluded = {n.lower() for n in EXCLUDED_FROM_STOP_ALL}
        
        cfg_rows = self._wrap_call(self._server_proxy.supervisor.getAllConfigInfo) or []
        cfg_by_name = {str(r.get('name')): r for r in cfg_rows if r.get('name')}

        def prio(name: str) -> int:
            try:
                return int(cfg_by_name.get(name, {}).get('priority', 9999))
            except Exception:
                return 9999
            
        items = self.list_processes()
        state_by_name = {p.name: (p.state or '').upper() for p in items}
        names_sorted = sorted(
            state_by_name.keys(),
            key=lambda n: (prio(n), n or ''),
            reverse=True)

        for name in names_sorted:
            if (name or '').lower() in excluded:
                continue

            state = state_by_name.get(name, '')
            if state in ('RUNNING', 'STARTING'):
                try:
                    self._wrap_call(self._server_proxy.supervisor.stopProcess, name)
                except Exception:
                    continue

        return None