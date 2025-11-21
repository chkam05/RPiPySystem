from __future__ import annotations
from flask import jsonify, request
from typing import ClassVar

from system_service.models.system.info.os_info import OSInfo
from system_service.models.system.processes.process_info import ProcessInfo
from system_service.models.system.processes.process_info_request import ProcessInfoRequest
from system_service.models.system.usage.cpu_info import CPUInfo
from system_service.models.system.users.os_user_info import OSUserInfo
from system_service.models.system.users.os_user_logged_in import OSUserLoggedIn
from system_service.utils.data_resolvers.os_info_resolver import OSInfoResolver
from system_service.utils.data_resolvers.os_usage_resolver import OSUsageResolver
from system_service.utils.data_resolvers.process_info_resolver import ProcessInfoResolver
from system_service.utils.data_resolvers.user_info_resolver import UserInfoResolver
from utils.api.auto_swag import auto_swag, get_bool_query_arg, ok, qparam, request_body_json, unauthorized
from utils.api.flask_api_service import FlaskApiService
from utils.api.mid_auth_controller import MidAuthController
from utils.data.dict_formatter import DictFormatter


class OSInfoController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_os_info'
    _CONTROLLER_PATH: ClassVar[str] = 'info'
    _USERS_F_USER_NAME: ClassVar[str] = 'name'
    _USERS_F_LOGGABLE_USERS: ClassVar[str] = 'loggable'

    def __init__(self, service: FlaskApiService, url_prefix_base: str, auth_url: str) -> None:
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> OSInfoController:
        self.add_url_rule('/', view_func=self.get_os_info, methods=['GET'])
        self.add_url_rule('/cpu', view_func=self.get_cpu_info, methods=['GET'])
        self.add_url_rule('/processes', view_func=self.get_processes, methods=['POST'])
        self.add_url_rule('/users', view_func=self.get_users, methods=['GET'])
        self.add_url_rule('/users/logged_in', view_func=self.get_logged_in_users, methods=['GET'])
        return self
    
    # --------------------------------------------------------------------------
    # --- ENDPOINTS ---
    # --------------------------------------------------------------------------

    @auto_swag(
        tags=['system'],
        summary='Get information about the operating system - Root Only',
        description='Returns information about the operating system on which the service is running (Root required).',
        responses={
            200: ok(OSInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_os_info(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        info = OSInfoResolver.get_os_info()
        return jsonify(info.to_public()), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get information about the processor - Root Only',
        description='Returns information about the processor (Root required).',
        responses={
            200: ok(CPUInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_cpu_info(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        cpu_info = OSUsageResolver.get_cpu_info()
        return jsonify(cpu_info.to_public()), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get list of current processes - Root Only',
        description='Returns list of processes currently running in system (Root required).',
        request_body=request_body_json(ProcessInfoRequest.schema_get_request()),
        responses={
            200: ok(ProcessInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_processes(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        
        raw_data = request.get_json(silent=True)
        data = ProcessInfoRequest.from_dict(raw_data) if raw_data else ProcessInfoRequest.default()

        processes = ProcessInfoResolver.get_process_infos(data)
        processes_dict = ProcessInfo.list_to_public(processes)
        keep_null_fields = [k for k, v in data.to_dict().items() if v is True]

        return jsonify(DictFormatter.clean_list(processes_dict, keep_null_fields)), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get system users - Root Only',
        description='Returns list of users available in the system (Root required).',
        parameters=[
            qparam(_USERS_F_USER_NAME, {'type': 'string', 'example': 'root'}, 'Username search phrase.'),
            qparam(_USERS_F_LOGGABLE_USERS, {'type': 'boolean', 'example': False}, 'Show only users who can log in to the system.')
        ],
        responses={
            200: ok(OSUserInfo.schema_public_list()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_users(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        
        user_name = request.args.get(
            self._USERS_F_USER_NAME,
            type=str,
            default=None
        )

        only_loggable_users = get_bool_query_arg(self._USERS_F_LOGGABLE_USERS, False)

        users = UserInfoResolver.get_system_users(only_loggable_users, user_name)
        return jsonify(OSUserInfo.list_to_dicts(users)), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get logged in system users - Root Only',
        description='Returns list of users that are logged in the system. (Root required)',
        parameters=[],
        responses={
            200: ok(OSUserLoggedIn.schema_public_list()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_logged_in_users(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        logged_in_users = UserInfoResolver.get_logged_in_users()
        return jsonify(OSUserLoggedIn.list_to_dicts(logged_in_users)), 200