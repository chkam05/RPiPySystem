from abc import abstractmethod
from typing import Iterable
from auth_service.models.access_level import AccessLevel
import requests

from utils.api.base_controller import BaseController
from utils.api.flask_api_service import FlaskApiService
from utils.mid_auth_controller import AuthCheckResult
from utils.security.bearer_reader import BearerReader


class MidAuthController(BaseController):
    """Base controller providing middleware-like authentication via remote auth service."""

    def __init__(
            self,
            name: str,
            import_name:
            str, url_prefix:
            str, auth_url: str,
            *,
            service: FlaskApiService
    ) -> None:
        """Initialize the controller with the auth URL and attach it to the service."""
        # Fields validation:
        if not isinstance(auth_url, str) or not auth_url.strip():
            raise ValueError('\"auth_url\" is required')
        
        self._auth_url = auth_url.strip()
        self.http = requests

        super().__init__(name, import_name, url_prefix, service=service)
    
    # --------------------------------------------------------------------------
    # --- AUTHENTICATION METHODS ---
    # --------------------------------------------------------------------------

    def _require_access(self, allowed: Iterable[AccessLevel], *, error_msg: str) -> AuthCheckResult:
        """Validate the Bearer token and check if the user has any of the allowed access levels."""
        headers = BearerReader.bearer_headers_from_request()
        if not headers:
            return False, {'message': 'missing bearer token'}, 401

        try:
            r = self.http.post(self._auth_url, headers=headers, timeout=3.0)
        except requests.RequestException:
            return False, {'message': 'auth service unreachable'}, 503

        if r.status_code != 200:
            # Treat any response other than 200 as an invalid/expired token.
            return False, {'message': 'invalid or expired token'}, 401

        try:
            payload = r.json() or {}
            user = payload.get('user') or {}
            level_str = user.get('level')
            level = AccessLevel.from_str(level_str)
        except Exception:
            return False, {'message': 'auth response malformed'}, 503

        if level not in set(allowed):
            return False, {'message': error_msg}, 403

        return True, None, 200
    
    # --------------------------------------------------------------------------
    # --- PRIVILEGE CHECKING METHODS ---
    # --------------------------------------------------------------------------

    def _require_root(self) -> AuthCheckResult:
        """Check if the requesting user has Root-level access."""
        return self._require_access(
            {AccessLevel.ROOT},
            error_msg='forbidden: requires Root privileges'
        )

    def _require_admin(self) -> AuthCheckResult:
        """Check if the requesting user has Admin-level access."""
        return self._require_access(
            {AccessLevel.ADMIN, AccessLevel.ROOT},
            error_msg='forbidden: requires Admin privileges'
        )

    def _require_auth(self) -> AuthCheckResult:
        """Check if the requesting user is authenticated with any valid access level."""
        return self._require_access(
            {AccessLevel.USER, AccessLevel.ADMIN, AccessLevel.ROOT},
            error_msg='forbidden: requires authentication'
        )
    
    # --------------------------------------------------------------------------
    # --- CONFIGURATION METHODS ---
    # --------------------------------------------------------------------------
    
    @abstractmethod
    def register_routes(self) -> BaseController:
        """Register all routes for this controller on the blueprint."""
        return self