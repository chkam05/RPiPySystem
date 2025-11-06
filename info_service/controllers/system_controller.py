from typing import ClassVar

from flask import jsonify
from info_service.models.system.os_info import OSInfo
from info_service.utils.os_info_resolver import OSInfoResolver
from utils.auto_swag import auto_swag, ok, unauthorized
from utils.mid_auth_controller import MidAuthController


class SystemController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'info_system'
    _CONTROLLER_PATH: ClassVar[str] = 'system'

    def __init__(self, url_prefix_base: str, auth_url: str) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> 'SystemController':
        self.add_url_rule('/info', view_func=self.get_info, methods=['GET'])
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

        iface = OSInfoResolver.get_os_info()
        return jsonify(iface.to_public()), 200