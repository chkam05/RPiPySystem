from typing import ClassVar

from flask import jsonify
from system_service.models.internal.interface_info import InterfaceInfo
from system_service.utils.network_interfaces_resolver import NetworkInterfacesResolver
from utils.auto_swag import auto_swag, ok, unauthorized
from utils.mid_auth_controller import MidAuthController


class InternalNetworkController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_network_internal'
    _CONTROLLER_PATH: ClassVar[str] = 'network/internal'

    def __init__(self, url_prefix_base: str, auth_url: str) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> 'InternalNetworkController':
        self.add_url_rule('/list', view_func=self.list_interfaces, methods=['GET'])
        self.add_url_rule('/<name>', view_func=self.get_interface, methods=['GET'])
        return self

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['network'],
        summary='Get network interface details — Root Only',
        description='Returns single internal network interface details.',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'eth0'},
            'required': True,
            'description': 'Interface Name'
        }],
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
        summary='Get detailed network interfaces list — Root Only',
        description='Returns detailed internal network interfaces list.',
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