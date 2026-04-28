from __future__ import annotations
from typing import ClassVar

from core.authorization.models.auth_check_result import AuthCheckResult
from core.data.error_response import ErrorResponse
from core.supervisor.models.supervisor_action_result import SupervisorActionResult
from flask import jsonify

from core.api.auto_swag import auto_swag, no_content, ok, pparam, unauthorized
from core.api.flask_api_service import FlaskApiService
from core.api.mid_auth_controller import MidAuthController
from core.supervisor.models.supervisor_service_info import SupervisorServiceInfo
from core.supervisor.supervisor_manager import SupervisorManager
from utilities.dict_formatter import DictFormatter


class SupervisorController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'Supervisor'
    _CONTROLLER_PATH: ClassVar[str] = 'supervisor'

    def __init__(
            self,
            service: FlaskApiService,
            supervisor_manager: SupervisorManager,
            auth_url: str,
            url_prefix_base: str
        ) -> None:
        # Arguments validation
        if not supervisor_manager:
            raise ValueError('"supervisor_manager" component is required.')
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"auth_url" argument is required (e.g.: "http://127.0.0.1/auth/validate").')
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"url_prefix_base" argument is required (e.g.: "/api").')
        
        self._supervisor_manager = supervisor_manager

        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, auth_url, url_prefix)
    
    def register_routes(self) -> SupervisorController:
        self.add_url_rule('/list', view_func=self.list_services, methods=['GET'])
        self.add_url_rule('/<name>', view_func=self.get_service_info, methods=['GET'])
        self.add_url_rule('/restart/<name>', view_func=self.restart_service, methods=['POST'])
        self.add_url_rule('/start/<name>', view_func=self.start_service, methods=['POST'])
        self.add_url_rule('/stop/<name>', view_func=self.stop_service, methods=['POST'])
        self.add_url_rule('/stop_all', view_func=self.stop_all_services, methods=['POST'])
        return self
    
    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Get Supervisor Service details - Root Only',
        description='Returns detailed Supervisor Service info for the given Service (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(SupervisorServiceInfo.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def get_service_info(self, name: str):
        auth_result: AuthCheckResult = self._require_root()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        details = self._supervisor_manager.get_service_details(name)
        return jsonify(details.to_public()), 200

    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='List Supervisor Services - Root Only',
        description='Returns the status and metadata for all Supervisord-managed Services in the microservice suite (Root required).',
        responses={
            200: ok(SupervisorServiceInfo.schema_public_short()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def list_services(self):
        auth_result: AuthCheckResult = self._require_root()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)
        
        processes = self._supervisor_manager.list_services()
        response = SupervisorServiceInfo.to_dict_list(processes)
        return jsonify(DictFormatter.clean_list(response)), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Restart Supervisord Service - Root Only',
        description='Restarts the specified Supervisord-managed Service, stopping it if running and then starting it again (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(SupervisorActionResult.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def restart_service(self, name: str):
        auth_result: AuthCheckResult = self._require_root()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)
        
        result = self._supervisor_manager.restart_service(name)
        return jsonify(result.to_public()), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Start Supervisor Service - Root Only',
        description='Starts the specified Supervisord-managed Service if it is not already running (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(SupervisorActionResult.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def start_service(self, name: str):
        auth_result: AuthCheckResult = self._require_root()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)
        
        result = self._supervisor_manager.start_service(name)
        return jsonify(result.to_public()), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Stop Supervisord Service - Root Only',
        description='Stops the specified Supervisord-managed Service gracefully (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(SupervisorActionResult.schema_public()),
            204: no_content('Process stopped; no content (controller exiting).'),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def stop_service(self, name: str):
        auth_result: AuthCheckResult = self._require_root()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)
        
        result = self._supervisor_manager.stop_service(name)
        return jsonify(result.to_public()), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Stop All Supervisord Services - Root Only',
        description='Stops all Supervisord-managed Services in the microservice suite gracefully (Root required).',
        responses={
            204: no_content('All eligible Services are being/been stopped. No content returned.'),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.'))
        },
    )
    def stop_all_services(self):
        auth_result: AuthCheckResult = self._require_root()
        if not auth_result.authenticated:
            return self._return_unauthorized_response(auth_result)

        self._supervisor_manager.stop_all_services()
        return '', 204
    