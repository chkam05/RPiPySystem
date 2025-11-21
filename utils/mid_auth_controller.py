from typing import Any, Dict, Iterable, Optional, Tuple
import json
import requests

from auth_service.models.access_level import AccessLevel
from utils.flask_api_service import FlaskApiService
from utils.security.bearer_reader import BearerReader

from .base_controller import BaseController


AuthCheckResult = Tuple[bool, Optional[Dict[str, Any]], int]


class MidAuthController(BaseController):
    
    def __init__(
            self,
            name: str,
            import_name:
            str, url_prefix:
            str, auth_url: str,
            *,
            service: Optional[FlaskApiService] = None) -> None:
        # Fields validation:
        if not isinstance(auth_url, str) or not auth_url.strip():
            raise ValueError('auth_url is required')
        
        self._auth_url = auth_url.strip()
        self.http = requests

        super().__init__(name, import_name, url_prefix, service=service)
    
    # --- Authentication methods ---

    def _require_access(self, allowed: Iterable[AccessLevel], *, error_msg: str) -> AuthCheckResult:
        headers = BearerReader.bearer_headers_from_request()
        if not headers:
            return False, {'message': 'missing bearer token'}, 401

        try:
            r = self.http.post(self._auth_url, headers=headers, timeout=3.0)
        except requests.RequestException:
            return False, {'message': 'auth service unreachable'}, 503

        if r.status_code != 200:
            # Treat any response other than 200 as an invalid/expired token
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

    # --- Public Require methods ---

    def _require_root(self) -> AuthCheckResult:
        return self._require_access(
            {AccessLevel.ROOT},
            error_msg='forbidden: requires Root privileges'
        )

    def _require_admin(self) -> AuthCheckResult:
        return self._require_access(
            {AccessLevel.ADMIN, AccessLevel.ROOT},
            error_msg='forbidden: requires Admin privileges'
        )

    def _require_auth(self) -> AuthCheckResult:
        return self._require_access(
            {AccessLevel.USER, AccessLevel.ADMIN, AccessLevel.ROOT},
            error_msg='forbidden: requires authentication'
        )
    
    # --- Contract: Derived classes must overload this method, as in BaseController ---
    def register_routes(self) -> 'MidAuthController':
        raise NotImplementedError(f'{self.__class__.__name__}.register_routes() must be overridden')