from __future__ import annotations
from flask import jsonify
from typing import ClassVar

from core.api.auto_swag import auto_swag, ok
from core.api.base_controller import BaseController
from core.api.flask_api_service import FlaskApiService
from core.data.health_response import HealthResponse


class HealthController(BaseController):
    _CONTROLLER_NAME: ClassVar[str] = 'Health'
    _CONTROLLER_PATH: ClassVar[str] = 'health'

    def __init__(self, service: FlaskApiService, url_prefix_base: str) -> None:
        # Arguments validation
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"url_prefix_base" argument is required (e.g.: "/api").')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, url_prefix)
    
    def register_routes(self) -> HealthController:
        self.add_url_rule('/health', view_func=self.health, methods=['GET'])
        return self
    
    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Health Check',
        description='Returns 200 with status to indicate the service is healthy.',
        security=[],    # Public
        responses={
            200: ok(HealthResponse.schema_public())
        }
    )
    def health(self):
        return jsonify(HealthResponse())
