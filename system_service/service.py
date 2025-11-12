from utils.flask_api_service import FlaskApiService


class SystemService(FlaskApiService):

    def __init__(self):
        from .config import HOST, PORT, SERVICE_NAME
        super().__init__(HOST, PORT, SERVICE_NAME)
    
    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    def _register_controllers(self):
        from .config import API_ENDPOINT, AUTH_URL
        from .controllers.health_controller import HealthController
        from .controllers.external_network_controller import ExternalNetworkController
        from .controllers.internal_network_controller import InternalNetworkController
        from .controllers.info_controller import InfoController
        from .controllers.usage_controller import UsageController

        base_url_prefix = API_ENDPOINT

        self._service.register_blueprint(HealthController(base_url_prefix))
        self._service.register_blueprint(ExternalNetworkController(base_url_prefix, AUTH_URL))
        self._service.register_blueprint(InternalNetworkController(base_url_prefix, AUTH_URL))
        self._service.register_blueprint(InfoController(base_url_prefix, AUTH_URL, self))
        self._service.register_blueprint(UsageController(base_url_prefix, AUTH_URL))