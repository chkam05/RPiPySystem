from typing import ClassVar

from flask import jsonify
from system_service.models.external.external_network_info import ExternalNetworkInfo
from system_service.utils.external_network_resolver import ExternalNetworkResolver
from utils.auto_swag import auto_swag, ok, unauthorized
from utils.mid_auth_controller import MidAuthController


class ExternalNetworkController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_network_external'
    _CONTROLLER_PATH: ClassVar[str] = 'network/external'

    def __init__(self, url_prefix_base: str, auth_url: str) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> 'ExternalNetworkController':
        self.add_url_rule('/', view_func=self.get_ext_net_info, methods=['GET'])
        return self

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['network'],
        summary='Get external network details — Root Only',
        description='Returns external network details (including public IP address).',
        responses={
            200: ok(ExternalNetworkInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_ext_net_info(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        ext_network_info = ExternalNetworkResolver.get_external_network_info()
        return jsonify(ext_network_info.to_public()), 200