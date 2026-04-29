from __future__ import annotations
from typing import ClassVar

from flask import jsonify

from core.api.auto_swag import auto_swag, ok, pparam, response
from core.api.flask_api_service import FlaskApiService
from core.api.mid_auth_controller import MidAuthController
from core.authorization.models.auth_check_result import AuthCheckResult
from core.data.error_response import ErrorResponse
from core.system.models import ExternalNetworkInfo, InterfaceInfo
from core.system.system_info import SystemInfo


class NetworkController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'Network'
    _CONTROLLER_PATH: ClassVar[str] = 'network'

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
    
    def register_routes(self) -> NetworkController:
        self.add_url_rule('/iface/list', view_func=self.get_iface_list, methods=['GET'])
        self.add_url_rule('/iface/<name>', view_func=self.get_iface, methods=['GET'])
        self.add_url_rule('/external', view_func=self.get_external_network_info, methods=['GET'])
        return self

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    @staticmethod
    def _select_fields(row: dict, fields: list[str]) -> dict:
        return {field: row.get(field) for field in fields}

    @staticmethod
    def _error_response(message: str, code: int, details: str):
        return jsonify(ErrorResponse(message=message, code=code, details=details).to_public()), code

    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='List Network Interfaces - Admin/Root Only',
        description='Returns a short list of network interfaces (Admin/Root required).',
        responses={
            200: ok(InterfaceInfo.schema_public_list()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_iface_list(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        fields = [
            InterfaceInfo.FIELD_NETWORK,
            InterfaceInfo.FIELD_DEVICE,
            InterfaceInfo.FIELD_INET,
            InterfaceInfo.FIELD_INET6,
        ]

        return jsonify([
            self._select_fields(interface.to_public(), fields)
            for interface in self._system_info.get_network_interfaces()
        ]), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Network Interface - Admin/Root Only',
        description='Returns full details for the given network interface (Admin/Root required).',
        parameters=[pparam('name', {'type': 'string', 'example': 'eth0'}, 'Network interface name')],
        responses={
            200: ok(InterfaceInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('Interface not found.', ErrorResponse.schema_public('not_found', 404, 'Interface not found.')),
        },
    )
    def get_iface(self, name: str):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        interface = self._system_info.get_network_interface(name)
        if interface is None:
            return self._error_response('Interface not found.', 404, f'Interface "{name}" was not found.')

        return jsonify(interface.to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get External Network Info - Admin/Root Only',
        description='Returns external public network address details (Admin/Root required).',
        responses={
            200: ok(ExternalNetworkInfo.schema_public()),
            401: response('Unauthorized.', ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            404: response('External address not found.', ErrorResponse.schema_public('not_found', 404, 'External address not found.')),
        },
    )
    def get_external_network_info(self):
        auth_result: AuthCheckResult = self._require_admin()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        info = self._system_info.get_external_network_info()
        if info is None:
            return self._error_response('External address not found.', 404, 'External address could not be resolved.')

        return jsonify(info.to_public()), 200
