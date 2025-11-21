from __future__ import annotations
from flask import jsonify
from typing import ClassVar

from system_service.models.supervisor.service_action_result import ServiceActionResult
from system_service.models.supervisor.service_details import ServiceDetails
from system_service.utils.supervisor.supervisor_proc_manager import SupervisorProcManager
from utils.api.base_controller import BaseController
from utils.api.flask_api_service import FlaskApiService
from utils.api.mid_auth_controller import MidAuthController
from utils.api.auto_swag import auto_swag, ok, unauthorized
from utils.auto_swag import pparam


class SupervisorController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_supervisor'
    _CONTROLLER_PATH: ClassVar[str] = 'supervisor'

    def __init__(
        self,
        service: FlaskApiService,
        url_prefix_base: str,
        auth_url: str,
        supervisor_proc_manager: SupervisorProcManager
    ) -> None:
        self._supervisor_proc_manager = supervisor_proc_manager
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)
        super().__init__(service, self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> SupervisorController:
        self.add_url_rule('/list', view_func=self.list_services, methods=['GET'])
        self.add_url_rule('/<name>', view_func=self.get_service_info, methods=['GET'])
        self.add_url_rule('/restart/<name>', view_func=self.restart_service, methods=['POST'])
        self.add_url_rule('/start/<name>', view_func=self.start_service, methods=['POST'])
        self.add_url_rule('/stop/<name>', view_func=self.stop_service, methods=['POST'])
        self.add_url_rule('/stop_all', view_func=self.stop_all_services, methods=['POST'])
        return self

    # --------------------------------------------------------------------------
    # --- ENDPOINTS ---
    # --------------------------------------------------------------------------

    @auto_swag(
        tags=['supervisor'],
        summary='List Supervisor Services - Root Only',
        description='Returns the status and metadata for all Supervisord-managed Services in the microservice suite (Root required).',
        responses={
            200: ok(ServiceDetails.schema_public_list()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def list_services(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        
        processes = self._supervisor_proc_manager.list_services()
        return jsonify(ServiceDetails.to_list_dicts(processes)), 200
    
    @auto_swag(
        tags=['supervisor'],
        summary='Get Supervisor Service details - Root Only',
        description='Returns detailed Supervisor Service info for the given Service (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(ServiceDetails.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_service_info(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        details = self._supervisor_proc_manager.service_details(name)
        return jsonify(details.to_public()), 200
    
    @auto_swag(
        tags=['supervisor'],
        summary='Restart Supervisord Service - Root Only',
        description='Restarts the specified Supervisord-managed Service, stopping it if running and then starting it again (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(ServiceActionResult.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def restart_service(self, name: str):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code
        
        result = self._supervisor_proc_manager.restart_service(name)
        return jsonify(result.to_public()), 200

    @auto_swag(
        tags=['supervisor'],
        summary='Start Supervisor Service - Root Only',
        description='Starts the specified Supervisord-managed Service if it is not already running (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(ServiceActionResult.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def start_service(self, name: str):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code
        
        result = self._supervisor_proc_manager.start_service(name)
        return jsonify(result.to_public()), 200
    
    @auto_swag(
        tags=['supervisor'],
        summary='Stop Supervisord Service - Root Only',
        description='Stops the specified Supervisord-managed Service gracefully (Root required).',
        parameters=[
            pparam('name', {'type': 'string', 'example': 'service_name'}, 'Service name')
        ],
        responses={
            200: ok(ServiceActionResult.schema_public()),
            204: {'description': 'Process stopped; no content (controller exiting).'},
            401: unauthorized('Missing/invalid token'),
        },
    )
    def stop_service(self, name: str):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code
        
        result = self._supervisor_proc_manager.stop_service(name)
        return jsonify(result.to_public()), 200
    
    @auto_swag(
        tags=['supervisor'],
        summary='Stop All Supervisord Services - Root Only',
        description='Stops all Supervisord-managed Services in the microservice suite gracefully (Root required).',
        responses={
            204: {'description': 'All eligible Services are being/been stopped. No content returned.'},
            401: unauthorized('Missing/invalid token')
        },
    )
    def stop_all_services(self):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code

        self._supervisor_proc_manager.stop_all_services()
        return '', 204