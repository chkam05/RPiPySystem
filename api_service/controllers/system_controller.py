from __future__ import annotations
from datetime import datetime
from typing import Any, ClassVar

from flask import jsonify, request

from core.api.auto_swag import auto_swag, ok, pparam, request_body_json, response
from core.api.flask_api_service import FlaskApiService
from core.api.mid_auth_controller import MidAuthController
from core.authorization.models.auth_check_result import AuthCheckResult
from core.data.error_response import ErrorResponse
from core.system.models import (
    CPUInfo,
    CPUUsage,
    DiskUsage,
    MemUsage,
    OSInfo,
    OSUsage,
    OSUserInfo,
    OSUserLoggedIn,
    ProcessInfo,
    ProcessListRequest,
    TemperatureInfo,
)
from core.system.system_info import SystemInfo


class SystemController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'System'
    _CONTROLLER_PATH: ClassVar[str] = 'system'

    def __init__(
            self,
            service: FlaskApiService,
            system_info: SystemInfo,
            auth_url: str,
            url_prefix_base: str
        ) -> None:
        # Arguments validation
        if not system_info:
            raise ValueError('"system_info" component is required.')
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"auth_url" argument is required (e.g.: "http://127.0.0.1/auth/validate").')
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"url_prefix_base" argument is required (e.g.: "/api").')

        self._system_info = system_info

        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, auth_url, url_prefix)
    
    def register_routes(self) -> SystemController:
        self.add_url_rule('/info/cpu', view_func=self.get_cpu_info, methods=['GET'])
        self.add_url_rule('/info/os', view_func=self.get_os_info, methods=['GET'])
        self.add_url_rule('/info/temperature', view_func=self.get_os_temperature, methods=['GET'])
        self.add_url_rule('/proc/list', view_func=self.get_processes_list, methods=['POST'])
        self.add_url_rule('/proc/<int:id>', view_func=self.get_process_by_id, methods=['GET'])
        self.add_url_rule('/usage/cpu', view_func=self.get_cpu_usage, methods=['GET'])
        self.add_url_rule('/usage/disk', view_func=self.get_disks_usage, methods=['GET'])
        self.add_url_rule('/usage/mem', view_func=self.get_mem_usage, methods=['GET'])
        self.add_url_rule('/usage/os', view_func=self.get_os_usage, methods=['GET'])
        self.add_url_rule('/users/list', view_func=self.get_users_list, methods=['GET'])
        self.add_url_rule('/users/active', view_func=self.get_logged_in_users, methods=['GET'])
        self.add_url_rule('/users/active/<name>', view_func=self.get_logged_in_user_by_id_or_name, methods=['GET'])
        self.add_url_rule('/users/<idname>', view_func=self.get_user_by_id_or_name, methods=['GET'])
        return self
    
    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    @staticmethod
    def _select_fields(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
        return {field: row.get(field) for field in fields}

    @staticmethod
    def _sort_rows(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
        if not fields:
            return rows

        return sorted(rows, key=lambda row: tuple(SystemController._sort_value(row.get(field)) for field in fields))

    @staticmethod
    def _sort_value(value: Any):
        if value is None:
            return (1, '')
        if isinstance(value, (int, float)):
            return (0, value)
        if isinstance(value, datetime):
            return (0, value.isoformat())

        return (0, str(value).casefold())

    @staticmethod
    def _normalize_process_fields(fields: list[str]) -> list[str]:
        aliases = {
            'id': ProcessInfo.FIELD_PROCESS_ID,
            'pid': ProcessInfo.FIELD_PROCESS_ID,
            'name': ProcessInfo.FIELD_PROCESS_NAME,
            'nazwa': ProcessInfo.FIELD_PROCESS_NAME,
            'process': ProcessInfo.FIELD_PROCESS_NAME,
            'user': ProcessInfo.FIELD_USER_NAME,
            'uzytkownik': ProcessInfo.FIELD_USER_NAME,
            'użytkownik': ProcessInfo.FIELD_USER_NAME,
        }
        normalized: list[str] = []
        available = set(ProcessInfo().to_dict().keys())
        for field in fields or ProcessListRequest().fields:
            key = str(field).strip()
            resolved = aliases.get(key.casefold(), key)
            if resolved in available and resolved not in normalized:
                normalized.append(resolved)

        return normalized or ProcessListRequest().fields

    @staticmethod
    def _error_response(message: str, code: int, details: str):
        return jsonify(ErrorResponse(message=message, code=code, details=details).to_public()), code

    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get CPU Info - Admin/Root Only',
        description='Returns CPU hardware details (Admin/Root required).',
        responses={
            200: ok(CPUInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_cpu_info(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(self._system_info.get_cpu_info().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get OS Info - Admin/Root Only',
        description='Returns operating system details (Admin/Root required).',
        responses={
            200: ok(OSInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_os_info(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(self._system_info.get_os_info().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get OS Temperature - Admin/Root Only',
        description='Returns current system temperature details (Admin/Root required).',
        responses={
            200: ok(TemperatureInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_os_temperature(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(self._system_info.get_temperature_info().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='List Processes - Admin/Root Only',
        description='Returns a selectable and sortable list of active processes (Admin/Root required).',
        request_body=request_body_json(ProcessListRequest.schema_public(), ProcessListRequest().to_dict(), required=False),
        responses={
            200: ok(ProcessInfo.schema_public_list()),
            400: response('Bad request.', ErrorResponse.schema_public('bad_request', 400, 'Invalid process list request.')),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_processes_list(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        data = request.get_json(silent=True) or {}
        list_request = ProcessListRequest.from_dict(data)
        fields = self._normalize_process_fields(list_request.fields)
        sort_fields = self._normalize_process_fields(list_request.sort)
        processes = self._sort_rows(ProcessInfo.to_public_list(self._system_info.get_processes()), sort_fields)
        return jsonify([self._select_fields(process, fields) for process in processes]), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Process By ID - Admin/Root Only',
        description='Returns full details for a process by PID (Admin/Root required).',
        parameters=[pparam('id', {'type': 'integer', 'example': 1234}, 'Process ID')],
        responses={
            200: ok(ProcessInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Process not found.', ErrorResponse.schema_public('not_found', 404, 'Process not found.')),
        },
    )
    def get_process_by_id(self, id: int):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        process = self._system_info.get_process_by_id(id)
        if process is None:
            return self._error_response('Process not found.', 404, f'Process "{id}" was not found.')

        return jsonify(process.to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get CPU Usage - Admin/Root Only',
        description='Returns current CPU usage (Admin/Root required).',
        responses={
            200: ok(CPUUsage.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_cpu_usage(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(self._system_info.get_cpu_usage().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Disk Usage - Admin/Root Only',
        description='Returns disk and swap usage list (Admin/Root required).',
        responses={
            200: ok(DiskUsage.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_disks_usage(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(DiskUsage.to_public_list(self._system_info.get_disks())), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Memory Usage - Admin/Root Only',
        description='Returns current RAM and swap usage (Admin/Root required).',
        responses={
            200: ok(MemUsage.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_mem_usage(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(self._system_info.get_memory_usage().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get OS Usage - Admin/Root Only',
        description='Returns grouped CPU, temperature, memory and disk usage (Admin/Root required).',
        responses={
            200: ok(OSUsage.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_os_usage(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify(self._system_info.get_os_usage().to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='List System Users - Admin/Root Only',
        description='Returns a short list of system users (Admin/Root required).',
        responses={
            200: ok(OSUserInfo.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_users_list(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        return jsonify([
            self._select_fields(user.to_public(), [OSUserInfo.FIELD_USER_ID, OSUserInfo.FIELD_USER_NAME])
            for user in self._system_info.get_users()
        ]), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get System User - Admin/Root Only',
        description='Returns full system user details by user ID or user name (Admin/Root required).',
        parameters=[pparam('idname', {'type': 'string', 'example': 'pi'}, 'User ID or user name')],
        responses={
            200: ok(OSUserInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('User not found.', ErrorResponse.schema_public('not_found', 404, 'User not found.')),
        },
    )
    def get_user_by_id_or_name(self, idname: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        user = self._system_info.get_user_by_id_or_name(idname)
        if user is None:
            return self._error_response('User not found.', 404, f'User "{idname}" was not found.')

        return jsonify(user.to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='List Logged-In Users - Admin/Root Only',
        description='Returns a short list of currently logged-in users (Admin/Root required).',
        responses={
            200: ok(OSUserLoggedIn.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_logged_in_users(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        fields = [
            OSUserLoggedIn.FIELD_USER_NAME,
            OSUserLoggedIn.FIELD_LOGGED_AT,
            OSUserLoggedIn.FIELD_TERMINAL_NAME,
        ]
        return jsonify([self._select_fields(user.to_public(), fields) for user in self._system_info.get_logged_in_users()]), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Logged-In User - Admin/Root Only',
        description='Returns full details for a logged-in user by name (Admin/Root required).',
        parameters=[pparam('name', {'type': 'string', 'example': 'pi'}, 'Logged-in user name')],
        responses={
            200: ok(OSUserLoggedIn.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Logged-in user not found.', ErrorResponse.schema_public('not_found', 404, 'Logged-in user not found.')),
        },
    )
    def get_logged_in_user_by_id_or_name(self, name: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        user = self._system_info.get_logged_in_user_by_id_or_name(name)
        if user is None:
            return self._error_response('Logged-in user not found.', 404, f'Logged-in user "{name}" was not found.')

        return jsonify(user.to_public()), 200
