import socket
from typing import Any, Dict, List, Optional, Tuple
from xmlrpc import client as xmlrpc_client

from system_service.config import EXCLUDED_FROM_STOP_ALL
from system_service.exceptions.supervisor_error import SupervisorError
from system_service.models.supervisor.service_action import ServiceAction
from system_service.models.supervisor.service_action_result import ServiceActionResult
from system_service.models.supervisor.service_details import ServiceDetails

class SupervisorProcManager:
    """Manage Supervisor processes via an XML-RPC ServerProxy."""

    def __init__(self, server_proxy: xmlrpc_client.ServerProxy):
        """Initialize the process manager with a Supervisor ServerProxy."""
        self._server_proxy = server_proxy
    
    # --------------------------------------------------------------------------
    # --- HELPER METHODS ---
    # --------------------------------------------------------------------------

    def _action_success(self, action: ServiceAction, info: Dict[str, Any]) -> Tuple[bool, str]:
        """Determine if a service action succeeded based on process info."""
        name = info.get('name')
        statename = (info.get('statename') or '').upper()

        if action == ServiceAction.START or action == ServiceAction.RESTART:
            ok = statename in ('STARTING', 'RUNNING')
            msg = f'{name} state={statename}'
            return ok, msg

        if action == ServiceAction.STOP:
            ok = statename in ('STOPPED', 'EXITED', 'FATAL', 'STOPPING')
            msg = f'{name} state={statename}'
            return ok, msg

        return False, f'{name} unknown state'
    
    @staticmethod
    def _wrap_call(fn, *args, **kwargs):
        """Call an XML-RPC function and normalize common Supervisor errors."""
        try:
            return fn(*args, **kwargs)
        except (ConnectionRefusedError, TimeoutError, socket.gaierror, socket.timeout, OSError) as e:
            raise SupervisorError(f'Supervisor xmlrpc unreachable: {e.__class__.__name__}') from e
        except xmlrpc_client.ProtocolError as e:
            raise SupervisorError(f'Supervisor protocol error: {e.errcode} {e.errmsg}') from e
        except xmlrpc_client.Fault as e:
            raise SupervisorError(f'Supervisor fault: {e.faultCode} {e.faultString}') from e
    
    # --------------------------------------------------------------------------
    # --- CONVERSION METHODS ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _to_optional_int(raw: Any) -> Optional[int]:
        """Convert a raw value to int, returning None on failure or zero."""
        if raw is None or raw == '':
            return None
        try:
            v = int(raw)
            return v if v != 0 else None
        except Exception:
            return None

    @staticmethod
    def _get_service_full_name(process_info: Dict[str, Any]) -> str:
        """Build a full service name from Supervisor process info."""
        base_name = str(process_info.get('name', '') or '').strip()
        group = str(process_info.get('group', '') or '').strip()
        return f"{group}:{base_name}" if group else base_name

    @classmethod
    def _create_service_details(cls, process_info: Dict[str, Any]) -> ServiceDetails:
        """Create a ServiceDetails instance from Supervisor process info."""
        return ServiceDetails(
            full_name=cls._get_service_full_name(process_info),
            name=str(process_info.get('name', '') or '').strip(),
            group=str(process_info.get('group', '') or '').strip(),
            state=process_info.get('statename', None),
            state_code=cls._to_optional_int(process_info.get('state', None)),
            pid=cls._to_optional_int(process_info.get('pid', None)),
            description=process_info.get('description', None),
            start=cls._to_optional_int(process_info.get('start', None)),
            stop=cls._to_optional_int(process_info.get('stop', None)),
            now=cls._to_optional_int(process_info.get('now', None)),
            exitstatus=cls._to_optional_int(process_info.get('exitstatus', None)),
            spawnerr=process_info.get('spawnerr', None),
            stdout_logfile=process_info.get('stdout_logfile', None),
            stderr_logfile=process_info.get('stderr_logfile', None),
        )

    # --------------------------------------------------------------------------
    # --- SERVICES MANAGEMENT ---
    # --------------------------------------------------------------------------

    def list_services(self) -> List[ServiceDetails]:
        """Return details for all services managed by Supervisor."""
        process_info_dict_list: List[Dict[str, Any]] = self._wrap_call(
            self._server_proxy.supervisor.getAllProcessInfo
        )

        return [
            self._create_service_details(p if isinstance(p, dict) else dict(p)) 
            for p in (process_info_dict_list or [])
        ]

    def service_details(self, name: str) -> ServiceDetails:
        """Return detailed information for a single service."""
        process_info_dict: Dict[str, Any] = dict(self._wrap_call(
            self._server_proxy.supervisor.getProcessInfo, name
        ))

        return self._create_service_details(process_info_dict)
    
    def start_service(self, name: str) -> ServiceActionResult:
        """Start a service and return the resulting action status."""
        self._wrap_call(self._server_proxy.supervisor.startProcess, name)
        info = self.info(name)
        ok, msg = self._action_success(ServiceAction.START, info)
        return ServiceActionResult(name=name, action=ServiceAction.START, state=ok, message=msg)
    
    def stop_service(self, name: str) -> ServiceActionResult:
        """Stop a service and return the resulting action status."""
        self._wrap_call(self._server_proxy.supervisor.stopProcess, name)
        info = self.info(name)
        ok, msg = self._action_success(ServiceAction.STOP, info)
        return ServiceActionResult(name=name, action=ServiceAction.STOP, state=ok, message=msg)

    def restart_service(self, name: str) -> ServiceActionResult:
        """Restart a service and return the resulting action status."""
        self.stop_service(name)
        self.start_service(name)
        info = self.info(name)
        ok, msg = self._action_success(ServiceAction.RESTART, info)
        return ServiceActionResult(name=name, action=ServiceAction.RESTART, state=ok, message=msg)
    
    def stop_all_services(self) -> None:
        """Stop all running services except those explicitly excluded."""
        excluded = {n.lower() for n in EXCLUDED_FROM_STOP_ALL}
        
        cfg_rows = self._wrap_call(self._server_proxy.supervisor.getAllConfigInfo) or []
        cfg_by_name = {str(r.get('name')): r for r in cfg_rows if r.get('name')}

        def prio(name: str) -> int:
            """Return process stop priority based on Supervisor config."""
            try:
                return int(cfg_by_name.get(name, {}).get('priority', 9999))
            except Exception:
                return 9999
            
        items = self.list_services()
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