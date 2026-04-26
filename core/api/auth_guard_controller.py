from typing import Optional

from .base_controller import BaseController
from .flask_api_service import FlaskApiService
from core.authorization.auth_guard import AuthGuard
from core.authorization.models.user import User


class AuthGuardController(BaseController):

    def __init__(
            self,
            service: FlaskApiService,
            auth_guard: AuthGuard,
            name: str,
            import_name: str,
            url_prefix: str) -> None:
        
        # Fields validation:
        if not auth_guard:
            raise ValueError('The "auth_guard" component is required.')

        self._auth_guard = auth_guard
        super().__init__(service, name, import_name, url_prefix)

    # --------------------------------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------------------------------

    @property
    def auth_guard(self):
        """Return the AuthGuard component."""
        return self._auth_guard
    