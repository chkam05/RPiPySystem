from core.api.flask_api_service import FlaskApiService


class ApiService(FlaskApiService):

    def __init__(self):
        from .config import (
            ACCESS_TOKEN_SECONDS, HOST, PORT, REFRESH_TOKEN_SECONDS,
            SECRET, SERVICE_NAME, SESSION_STORAGE_PATH, USER_STORAGE_PATH
        )
        from core.authorization.auth_guard import AuthGuard
        from core.authorization.storage.session_storage import SessionStorage
        from core.authorization.storage.user_storage import UserStorage
        
        self._sessions_storage = SessionStorage(SESSION_STORAGE_PATH)
        self._users_storage = UserStorage(USER_STORAGE_PATH)
        self._auth_guard = AuthGuard(
            ACCESS_TOKEN_SECONDS,
            REFRESH_TOKEN_SECONDS,
            SECRET,
            self._sessions_storage,
            self._users_storage)

        super().__init__(HOST, PORT, SERVICE_NAME)
    
    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    def _register_controllers(self):
        from .config import ROUTE
        from .controllers.auth_controller import AuthController
        from .controllers.health_controller import HealthController
        #from .controllers.sessions_controller import SessionsController
        #from .controllers.users_controller import UsersController

        base_url_prefix = ROUTE

        AuthController(self, self._auth_guard, base_url_prefix)
        HealthController(self, base_url_prefix)
        #self._service.register_blueprint(SessionsController(
        #    base_url_prefix, self._auth_guard, self._sessions_storage, self._users_storage))
        #self._service.register_blueprint(UsersController(
        #    base_url_prefix, self._auth_guard, self._users_storage))