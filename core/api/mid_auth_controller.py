from abc import abstractmethod
from flask import Response, jsonify
from typing import Iterable, Tuple
import requests

from .base_controller import BaseController
from .flask_api_service import FlaskApiService
from core.authorization.bearer_reader import BearerReader
from core.authorization.enums.access_level import AccessLevel
from core.authorization.models.auth_check_result import AuthCheckResult


class MidAuthController(BaseController):
    """Base controller providing middleware-like authentication via remote auth service."""

    def __init__(
        self,
        service: FlaskApiService,
        name: str,
        import_name: str,
        auth_url: str,
        url_prefix: str
    ) -> None:
        """Initialize the controller with the auth URL and attach it to the service."""

        # Arguments validation
        if not isinstance(auth_url, str) or not auth_url.strip():
            raise ValueError('\"auth_url\" is required.')
        
        self._auth_url = auth_url.strip()
        self.http = requests

        super().__init__(service, name, import_name, url_prefix)
    
    # --------------------------------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------------------------------

    def _require_access(self, allowed: Iterable[AccessLevel], *, error_msg: str) -> AuthCheckResult:
        """Validate the Bearer token and check if the user has any of the allowed access levels."""
        headers = BearerReader.bearer_headers_from_request()
        if not headers:
            return AuthCheckResult(False, 401, 'Missing bearer token.')

        try:
            r = self.http.post(self._auth_url, headers=headers, timeout=3.0)
        except requests.RequestException:
            return AuthCheckResult(False, 503, 'Auth service unreachable.')

        if r.status_code != 200:
            # Treat any response other than 200 as an invalid/expired token.
            return AuthCheckResult(False, 401, 'Invalid or expired token.')

        try:
            payload = r.json() or {}
            user = payload.get('user') or {}
            level_str = user.get('level')
            level = AccessLevel.from_str(level_str)
        except Exception:
            return AuthCheckResult(False, 503, 'Auth response malformed.')

        if level not in set(allowed):
            return AuthCheckResult(False, 403, error_msg)

        return AuthCheckResult(True, 200, None)
    
    def _require_auth(self) -> AuthCheckResult:
        """Check if the requesting user is authenticated with any valid access level."""
        return self._require_access(
            AccessLevel.get_all(),
            'You do not have permission to perform this action.'
        )

    def _require_root(self) -> AuthCheckResult:
        """Check if the requesting user has Root-level access."""
        return self._require_access(
            {AccessLevel.ROOT},
            error_msg='You do not have permission to perform this action (Root privileges required).'
        )

    def _require_admin(self) -> AuthCheckResult:
        """Check if the requesting user has Admin-level access."""
        return self._require_access(
            {AccessLevel.ADMIN, AccessLevel.ROOT},
            error_msg='You do not have permission to perform this action (Admin privileges required).'
        )
    
    @staticmethod
    def _return_unauthorized_response(result: AuthCheckResult) -> Tuple[Response, int]:
        return jsonify(result.to_error_response()), result.error_code

    # --------------------------------------------------------------------------------
    # CONFIGURATION METHODS
    # --------------------------------------------------------------------------------

    @abstractmethod
    def register_routes(self) -> BaseController:
        """Register all routes for this controller on the blueprint."""
        return self
