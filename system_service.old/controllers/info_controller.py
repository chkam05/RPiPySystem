from typing import ClassVar

from flask import jsonify, request
from supervisor_service.models.process_info import ProcessInfo
from system_service.models.system.disk_usage import DiskUsage
from system_service.models.system.mem_usage import MemUsage
from system_service.models.system.os_info import OSInfo
from system_service.models.system.os_temp_info import OSTempInfo
from system_service.models.system.os_usage import OSUsage
from system_service.models.system.cpu_info import CPUInfo
from system_service.models.system.cpu_usage import CPUUsage
from system_service.models.system.process_info_request import ProcessInfoRequest
from system_service.models.system.user_info import UserInfo
from system_service.models.system.user_logged_in import UserLoggedIn
from system_service.utils.os_info_resolver import OSInfoResolver
from system_service.utils.os_usage_resolver import OSUsageResolver
from system_service.utils.process_info_resolver import ProcessInfoResolver
from system_service.utils.user_info_resolver import UserInfoResolver
from utils.auto_swag import auto_swag, get_bool_query_arg, ok, qparam, request_body_json, unauthorized
from utils.flask_api_service import FlaskApiService
from utils.format_util import FormatUtil
from utils.mid_auth_controller import MidAuthController


class InfoController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_info'
    _CONTROLLER_PATH: ClassVar[str] = 'info'
    _USERS_F_USER_NAME: ClassVar[str] = 'name'
    _USERS_F_LOGGABLE_USERS: ClassVar[str] = 'loggable'

    def __init__(self, url_prefix_base: str, auth_url: str) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> 'InfoController':
        self.add_url_rule('/', view_func=self.get_info, methods=['GET'])
        self.add_url_rule('/cpu', view_func=self.get_cpu_info, methods=['GET'])
        self.add_url_rule('/processes', view_func=self.get_processes, methods=['POST'])
        self.add_url_rule('/users', view_func=self.get_users, methods=['GET'])
        self.add_url_rule('/users_logged_in', view_func=self.get_users_logged_in, methods=['GET'])
        return self

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['system'],
        summary='Get information about the operating system — Root Only',
        description='Returns information about the operating system on which the service is running.',
        responses={
            200: ok(OSInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_info(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        info = OSInfoResolver.get_os_info()
        return jsonify(info.to_public()), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get information about the processor — Root Only',
        description='Returns information about the processor.',
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
        summary='Get list of current processes — Root Only',
        description='Returns list of processes currently running in system.',
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

        return jsonify(FormatUtil.list_without_nulls(processes_dict, keep_null_fields)), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get system users — Root Only',
        description='Returns list of users available in the system.',
        parameters=[
            qparam(_USERS_F_USER_NAME, {'type': 'string', 'example': 'root'}, 'Username search phrase.'),
            qparam(_USERS_F_LOGGABLE_USERS, {'type': 'boolean', 'example': False}, 'Show only users who can log in to the system.')
        ],
        responses={
            200: ok(UserInfo.schema_public_list()),
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
        return jsonify(UserInfo.list_to_dicts(users)), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get logged in system users — Root Only',
        description='Returns list of users that are logged in the system.',
        parameters=[],
        responses={
            200: ok(UserLoggedIn.schema_public_list()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_users_logged_in(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        logged_in_users = UserInfoResolver.get_logged_in_users()
        return jsonify(UserLoggedIn.list_to_dicts(logged_in_users)), 200