from flask import jsonify, request
from typing import ClassVar, Optional
import requests

from auth_service.models.access_level import AccessLevel
from supervisor_service.models.process_action_result import ProcessActionResult
from supervisor_service.models.process_details import ProcessDetails
from supervisor_service.models.process_info import ProcessInfo
from supervisor_service.utils.processes_manager import ProcessesManager
from utils.auto_swag import auto_swag, ok, unauthorized
from utils.flask_api_service import FlaskApiService
from utils.mid_auth_controller import MidAuthController
from utils.security import SecurityUtils


class ProcessesController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'supervisor_processes'
    _CONTROLLER_PATH: ClassVar[str] = 'processes'

    def __init__(
            self,
            url_prefix_base: str,
            auth_url: str,
            processes_manager: ProcessesManager,
            *,
            service: Optional[FlaskApiService] = None) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        if not processes_manager:
            raise ValueError('processes_manager is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        self._processes_manager = processes_manager
        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url, service=service)
    
    def register_routes(self) -> 'ProcessesController':
        self.add_url_rule('/list', view_func=self.list_processes, methods=['GET'])
        self.add_url_rule('/<name>', view_func=self.get_process_info, methods=['GET'])
        self.add_url_rule('/<name>/start', view_func=self.start_process, methods=['POST'])
        self.add_url_rule('/<name>/stop', view_func=self.stop_process, methods=['POST'])
        self.add_url_rule('/<name>/restart', view_func=self.restart_process, methods=['POST'])
        self.add_url_rule('/stop_all', view_func=self.stop_all, methods=['POST'])
        return self
    
    # --- Utilities ---

    def _exec(self, fn, *args, **kwargs):
        try:
            return jsonify(fn(*args, **kwargs)), 200
        except RuntimeError as e:
            return jsonify({'message': str(e)}), 503

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['processes'],
        summary='List Supervisord Processes — Root Only',
        description='Returns the status and basic metadata for all Supervisord-managed services in the microservice suite (Root required).',
        responses={
            200: ok(ProcessInfo.schema_public_list()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def list_processes(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        
        processes = self._processes_manager.list_processes()
        return jsonify(ProcessInfo.list_to_public(processes)), 200
    
    @auto_swag(
        tags=['processes'],
        summary='Get process details — Root Only',
        description='Returns detailed Supervisor process info for the given process.',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'service_name'},
            'required': True,
            'description': 'Service name'
        }],
        responses={
            200: ok(ProcessDetails.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_process_info(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        details = self._processes_manager.info(name)
        return jsonify(details.to_public()), 200

    @auto_swag(
        tags=['processes'],
        summary='Start Supervisord Process — Root Only',
        description='Starts the specified Supervisord-managed service if it is not already running (Root required).',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'service_name'},
            'required': True,
            'description': 'Service name'
        }],
        responses={
            200: ok(ProcessActionResult.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def start_process(self, name: str):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code
        
        result = self._processes_manager.start(name)
        return jsonify(result.to_public()), 200

    @auto_swag(
        tags=['processes'],
        summary='Stop Supervisord Process — Root Only',
        description='Stops the specified Supervisord-managed service gracefully (Root required).',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'service_name'},
            'required': True,
            'description': 'Service name'
        }],
        responses={
            200: ok(ProcessActionResult.schema_public()),
            204: {'description': 'Process stopped; no content (controller exiting).'},
            401: unauthorized('Missing/invalid token'),
        },
    )
    def stop_process(self, name: str):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code
        
        if (name or '').lower() == self._service.name.lower():
            try:
                self._processes_manager._wrap_call(self._processes_manager._server_proxy.supervisor.stopProcess, name)
            except Exception:
                pass
            return '', 204
        
        result = self._processes_manager.stop(name)
        return jsonify(result.to_public()), 200

    @auto_swag(
        tags=['processes'],
        summary='Restart Supervisord Process — Root Only',
        description='Restarts the specified Supervisord-managed service, stopping it if running and then starting it again (Root required).',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'service_name'},
            'required': True,
            'description': 'Service name'
        }],
        responses={
            200: ok(ProcessActionResult.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def restart_process(self, name: str):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code
        
        result = self._processes_manager.restart(name)
        return jsonify(result.to_public()), 200

    @auto_swag(
        tags=['processes'],
        summary='Stop All Supervisord Processes — Root Only',
        description='Stops all Supervisord-managed services in the microservice suite gracefully (Root required).',
        responses={
            204: {'description': 'All eligible processes are being/been stopped. No content returned.'},
            401: unauthorized('Missing/invalid token')
        },
    )
    def stop_all(self):
        ok_, err, code = self._require_admin()
        if not ok_:
            return jsonify(err), code

        self._processes_manager.stop_all()
        return '', 204