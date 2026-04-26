from auth_service.storage.sessions_storage import SessionsStorage
from auth_service.storage.users_storage import UsersStorage
from auth_service.utils.auth_guard import AuthGuard
from utils.flask_api_service import FlaskApiService


class AuthService(FlaskApiService):

    def __init__(self):
        from .config import (
            ACCESS_TOKEN_SECONDS, HOST, PORT, REFRESH_TOKEN_SECONDS,
            SECRET, SERVICE_NAME, SESSIONS_STORAGE_PATH, USERS_STORAGE_PATH
        )
        
        self._sessions_storage = SessionsStorage(SESSIONS_STORAGE_PATH)
        self._users_storage = UsersStorage(USERS_STORAGE_PATH)
        self._auth_guard = AuthGuard(ACCESS_TOKEN_SECONDS, REFRESH_TOKEN_SECONDS, SECRET, self._users_storage)

        super().__init__(HOST, PORT, SERVICE_NAME)
    
    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    def _register_controllers(self):
        from .config import API_ENDPOINT
        from .controllers.health_controller import HealthController
        from .controllers.sessions_controller import SessionsController
        from .controllers.users_controller import UsersController

        base_url_prefix = API_ENDPOINT

        self._service.register_blueprint(HealthController(base_url_prefix))
        self._service.register_blueprint(SessionsController(
            base_url_prefix, self._auth_guard, self._sessions_storage, self._users_storage))
        self._service.register_blueprint(UsersController(
            base_url_prefix, self._auth_guard, self._users_storage))