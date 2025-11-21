from __future__ import annotations
from flask import jsonify
from typing import ClassVar

from utils.api.base_controller import BaseController
from utils.api.flask_api_service import FlaskApiService
from utils.auto_swag import auto_swag, object_schema, ok


class HealthController(BaseController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_health'
    _CONTROLLER_PATH: ClassVar[str] = 'health'

    def __init__(self, service: FlaskApiService, url_prefix_base: str) -> None:
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, url_prefix)
    
    def register_routes(self) -> HealthController:
        self.add_url_rule('/health', view_func=self.health, methods=['GET'])
        return self

    # --------------------------------------------------------------------------
    # --- ENDPOINTS ---
    # --------------------------------------------------------------------------

    @auto_swag(
        tags=['health'],
        summary='Health Check',
        description='Returns 200 with {"status":"ok"} to indicate the service is healthy.',
        security=[],    # Public
        responses={
            200: ok(object_schema({'status': {'type': 'string', 'example': 'ok'}}))
        }
    )
    def health(self):
        return jsonify({'status': 'ok'})