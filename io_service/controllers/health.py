from flask import Blueprint, jsonify
from utils.auto_swag import auto_swag, ok, object_schema
from utils.base_controller import BaseController


class HealthController(BaseController):
    def __init__(self, *, url_prefix: str = '/api/io') -> None:
        super().__init__('io_health', __name__, url_prefix=url_prefix)
    
    @auto_swag(
        tags=['health'],
        summary='Health check',
        security=[],    # Public
        responses={
            200: ok(object_schema({'status': {'type': 'string', 'example': 'ok'}}))
        }
    )
    def health(self):
        return jsonify({'status': 'ok'})
    
    def register_routes(self) -> 'HealthController':
        self.add_url_rule('/health', view_func=self.health, methods=['GET'])
        return self
