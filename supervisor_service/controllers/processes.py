from typing import Optional, Tuple
import os
import requests
from flask import jsonify, request

from auth_service.models.user import User
from supervisor_service.utils.process_manager import ProcessManager
from supervisor_service.config import AUTH_BASE_URL, AUTH_VALIDATION_ENDPOINT
from utils.base_controller import BaseController
from utils.auto_swag import auto_swag, ok, unauthorized
from utils.security import bearer_headers_from_request 


class ProcessesController(BaseController):
    def __init__(
            self, 
            *, 
            url_prefix: str = "/api/supervisor/processes", 
            process_manager: ProcessManager | None = None,
            auth_base_url: str | None = None,
            session: requests.sessions.Session | None = None):
        super().__init__("supervisor_processes", __name__, url_prefix=url_prefix)
        self.pm = process_manager or ProcessManager()
        self.auth_base_url = auth_base_url or AUTH_BASE_URL
        self.http = session or requests.Session()
    
    # region --- Auth helper methods ---
    
    def _require_root(self):
        headers = bearer_headers_from_request()
        
        if not headers:
            return False, {"message": "missing bearer token"}, 401

        try:
            url = f"{self.auth_base_url}/api/auth/session/validate"
            r = self.http.post(url, headers=headers, timeout=3.0)
        except requests.RequestException:
            return False, {"message": "auth service unreachable"}, 503

        if r.status_code != 200:
            return False, {"message": "invalid or expired token"}, 401

        try:
            payload = r.json()
            level = (payload.get("user") or {}).get("level")
        except Exception:
            return False, {"message": "auth response malformed"}, 503

        if level != "Root":
            return False, {"message": "forbidden: requires Root"}, 403

        return True, None, 200
    
    # endregion --- Auth helper methods ---

    def _exec(self, fn, *args, **kwargs):
        try:
            return jsonify(fn(*args, **kwargs)), 200
        except RuntimeError as e:
            return jsonify({"message": str(e)}), 503

    @auto_swag(
        tags=["supervisor"],
        summary="List processes (Root only)",
        responses={
            200: ok(
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "state": {"type": "string"},
                            "pid": {"type": "integer", "nullable": True},
                        }
                    }
                }
            ),
            401: unauthorized("Missing/invalid token"),
        },
    )
    def list_processes(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.list_processes)

    @auto_swag(
        tags=["supervisor"],
        summary="Start process (Root only)",
        parameters=[{
            "in": "path",
            "name": "name",
            "schema": {"type": "string", "example": "service_name"},
            "required": True,
            "description": "Service name"
        }],
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "started": {"type": "boolean"},
                        "message": {"type": "string"},
                    },
                }
            ),
            401: unauthorized("Missing/invalid token"),
        },
    )
    def start_process(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.start, name)

    @auto_swag(
        tags=["supervisor"],
        summary="Stop process (Root only)",
        parameters=[{
            "in": "path",
            "name": "name",
            "schema": {"type": "string", "example": "service_name"},
            "required": True,
            "description": "Service name"
        }],
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "stopped": {"type": "boolean"},
                        "message": {"type": "string"},
                    },
                }
            ),
            401: unauthorized("Missing/invalid token"),
        },
    )
    def stop_process(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.stop, name)

    @auto_swag(
        tags=["supervisor"],
        summary="Restart process (Root only)",
        parameters=[{
            "in": "path",
            "name": "name",
            "schema": {"type": "string", "example": "service_name"},
            "required": True,
            "description": "Service name"
        }],
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "restarted": {"type": "boolean"},
                        "message": {"type": "string"},
                    },
                }
            ),
            401: unauthorized("Missing/invalid token"),
        },
    )
    def restart_process(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.restart, name)

    @auto_swag(
        tags=["supervisor"],
        summary="Stop all processes (Root only)",
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "stopped": {"type": "integer", "description": "How many were stopped"}
                    },
                }
            ),
            401: unauthorized("Missing/invalid token"),
        },
    )
    def stop_all(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.stop_all)

    # region --- Endpoint registration ---

    def register_routes(self) -> "ProcessesController":
        self.add_url_rule("/list", view_func=self.list_processes, methods=["GET"])
        self.add_url_rule("/<name>/start", view_func=self.start_process, methods=["POST"])
        self.add_url_rule("/<name>/stop", view_func=self.stop_process, methods=["POST"])
        self.add_url_rule("/<name>/restart", view_func=self.restart_process, methods=["POST"])
        self.add_url_rule("/stop_all", view_func=self.stop_all, methods=["POST"])
        return self

    # endregion --- Endpoint registration ---
