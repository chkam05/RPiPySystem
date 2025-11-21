from __future__ import annotations
from flask import jsonify
from typing import ClassVar

from system_service.models.network.external.external_network_info import ExternalNetworkInfo
from system_service.models.network.internal.interface_info import InterfaceInfo
from system_service.utils.data_resolvers.external_network_resolver import ExternalNetworkResolver
from system_service.utils.data_resolvers.network_interfaces_resolver import NetworkInterfacesResolver
from utils.api.auto_swag import auto_swag, ok, pparam, unauthorized
from utils.api.flask_api_service import FlaskApiService
from utils.api.mid_auth_controller import MidAuthController


class NetworkController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_network'
    _CONTROLLER_PATH: ClassVar[str] = 'network'

    def __init__(self, service: FlaskApiService, url_prefix_base: str, auth_url: str) -> None:
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> NetworkController:
        self.add_url_rule('/external', view_func=self.get_external_network_info, methods=['GET'])
        self.add_url_rule('/internal/<name>', view_func=self.get_interface, methods=['GET'])
        self.add_url_rule('/internal/list', view_func=self.list_interfaces, methods=['GET'])
        return self

    # --------------------------------------------------------------------------
    # --- ENDPOINTS ---
    # --------------------------------------------------------------------------

    @auto_swag(
        tags=['network'],
        summary='Get external network details - Root Only',
        description='Returns external network details (including public IP address, Root required).',
        responses={
            200: ok(ExternalNetworkInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_external_network_info(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        ext_network_info = ExternalNetworkResolver.get_external_network_info()
        return jsonify(ext_network_info.to_public()), 200
    
    @auto_swag(
        tags=['network'],
        summary='Get network interface details - Root Only',
        description='Returns single internal network interface details (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'eth0'}, 'Interface name')
        ],
        responses={
            200: ok(InterfaceInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_interface(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        iface = NetworkInterfacesResolver.get_network_interface(name)
        return jsonify(iface.to_public()), 200

    @auto_swag(
        tags=['network'],
        summary='Get detailed network interfaces list - Root Only',
        description='Returns detailed internal network interfaces list (Root required).',
        responses={
            200: ok(InterfaceInfo.schema_public_list()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def list_interfaces(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        
        ifaces = NetworkInterfacesResolver.get_network_interfaces()
        return jsonify(InterfaceInfo.list_to_public(ifaces)), 200