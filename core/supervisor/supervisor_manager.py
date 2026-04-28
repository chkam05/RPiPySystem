from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional
from xmlrpc import client as xmlrpc_client

from core.supervisor.enums.supervisor_action import SupervisorAction
from core.supervisor.enums.supervisor_method import SupervisorMethod
from core.supervisor.enums.supervisor_process_state import SupervisorProcessState
from core.supervisor.models.supervisor_action_result import SupervisorActionResult
from core.supervisor.models.supervisor_service_info import SupervisorServiceInfo
from core.supervisor.supervisor_connection import SupervisorConnection


DEFAULT_EXCLUDED_FROM_STOP_ALL = frozenset({'event_listener'})


class SupervisorManager:
    """Manage Supervisor processes through SupervisorConnection."""

    def __init__(
        self,
        connection: SupervisorConnection | xmlrpc_client.ServerProxy,
        *,
        excluded_from_stop_all: Optional[Iterable[str]] = None,
    ) -> None:
        if isinstance(connection, SupervisorConnection):
            self._connection = connection
        else:
            self._connection = SupervisorConnection(server_proxy=connection)

        excluded = DEFAULT_EXCLUDED_FROM_STOP_ALL if excluded_from_stop_all is None else excluded_from_stop_all
        self._excluded_from_stop_all = {name.lower() for name in excluded}

    # --------------------------------------------------------------------------------
    # CONVERSION METHODS
    # --------------------------------------------------------------------------------

    @staticmethod
    def _to_optional_int(raw: Any) -> Optional[int]:
        if raw is None or raw == '':
            return None
        try:
            value = int(raw)
            return value if value != 0 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_service_full_name(process_info: Dict[str, Any]) -> str:
        name = str(process_info.get('name', '') or '').strip()
        group = str(process_info.get('group', '') or '').strip()
        return f'{group}:{name}' if group else name

    @classmethod
    def _create_service_summary(cls, process_info: Dict[str, Any]) -> SupervisorServiceInfo:
        return SupervisorServiceInfo(
            full_name=cls._get_service_full_name(process_info),
            name=str(process_info.get('name', '') or '').strip(),
            group=str(process_info.get('group', '') or '').strip(),
        )

    @classmethod
    def _create_service_details(cls, process_info: Dict[str, Any]) -> SupervisorServiceInfo:
        return SupervisorServiceInfo(
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
    
    # --------------------------------------------------------------------------------
    # SERVICES MANAGEMENT
    # --------------------------------------------------------------------------------

    def get_service_details(self, name: str) -> SupervisorServiceInfo:
        """Return detailed information for a single Supervisor service."""
        process_info = dict(self._connection.supervisor_call(SupervisorMethod.GET_PROCESS_INFO, name))
        return self._create_service_details(process_info)

    def list_services(self) -> List[SupervisorServiceInfo]:
        """Return service summaries with only full_name, name and group filled."""
        process_rows = self._connection.supervisor_call(SupervisorMethod.GET_ALL_PROCESS_INFO) or []
        return [
            self._create_service_summary(row if isinstance(row, dict) else dict(row))
            for row in process_rows
        ]

    def restart_service(self, name: str) -> SupervisorActionResult:
        """Restart a service and return the resulting action status."""
        self.stop_service(name)
        self.start_service(name)
        info = self._get_raw_service_info(name)
        ok, message = self._connection.action_success(SupervisorAction.RESTART, info)
        return SupervisorActionResult(name=name, action=SupervisorAction.RESTART, state=ok, message=message)

    def start_service(self, name: str) -> SupervisorActionResult:
        """Start a service and return the resulting action status."""
        self._connection.supervisor_call(SupervisorMethod.START_PROCESS, name)
        info = self._get_raw_service_info(name)
        ok, message = self._connection.action_success(SupervisorAction.START, info)
        return SupervisorActionResult(name=name, action=SupervisorAction.START, state=ok, message=message)

    def stop_service(self, name: str) -> SupervisorActionResult:
        """Stop a service and return the resulting action status."""
        self._connection.supervisor_call(SupervisorMethod.STOP_PROCESS, name)
        info = self._get_raw_service_info(name)
        ok, message = self._connection.action_success(SupervisorAction.STOP, info)
        return SupervisorActionResult(name=name, action=SupervisorAction.STOP, state=ok, message=message)

    def stop_all_services(self) -> None:
        """Stop all running services except those explicitly excluded."""
        config_rows = self._connection.supervisor_call(SupervisorMethod.GET_ALL_CONFIG_INFO) or []
        config_by_name = {
            str(row.get('name')): row
            for row in config_rows
            if isinstance(row, dict) and row.get('name')
        }

        process_rows = self._connection.supervisor_call(SupervisorMethod.GET_ALL_PROCESS_INFO) or []
        services = [
            row if isinstance(row, dict) else dict(row)
            for row in process_rows
        ]

        names_sorted = sorted(
            services,
            key=lambda row: (self._get_stop_priority(row, config_by_name), row.get('name') or ''),
            reverse=True,
        )

        for row in names_sorted:
            name = str(row.get('name') or '')
            full_name = self._get_service_full_name(row)
            state = str(row.get('statename') or '').upper()

            if self._is_excluded_from_stop_all(name, full_name):
                continue

            if state in (SupervisorProcessState.RUNNING.value, SupervisorProcessState.STARTING.value):
                try:
                    self._connection.supervisor_call(SupervisorMethod.STOP_PROCESS, full_name)
                except Exception:
                    continue

        return None

    # --------------------------------------------------------------------------------
    # HELPER METHODS
    # --------------------------------------------------------------------------------

    @staticmethod
    def _get_stop_priority(row: Dict[str, Any], config_by_name: Dict[str, Dict[str, Any]]) -> int:
        name = str(row.get('name') or '')
        full_name = SupervisorManager._get_service_full_name(row)

        try:
            return int(config_by_name.get(full_name, config_by_name.get(name, {})).get('priority', 9999))
        except (TypeError, ValueError):
            return 9999

    def _get_raw_service_info(self, name: str) -> Dict[str, Any]:
        return dict(self._connection.supervisor_call(SupervisorMethod.GET_PROCESS_INFO, name))

    def _is_excluded_from_stop_all(self, name: str, full_name: str) -> bool:
        return name.lower() in self._excluded_from_stop_all or full_name.lower() in self._excluded_from_stop_all
