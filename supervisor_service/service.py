from supervisor_service.utils.processes_manager import ProcessesManager
from supervisor_service.utils.supervisor_proxy_factory import SupervisorProxyFactory
from utils.flask_api_service import FlaskApiService


class SupervisorService(FlaskApiService):

    def __init__(self):
        from .config import HOST, PORT, SERVICE_NAME

        self._processes_manager = self._configure_process_manager()

        super().__init__(HOST, PORT, SERVICE_NAME)
    
    @staticmethod
    def _configure_process_manager() -> ProcessesManager:
        from .config import SOC_URL, SOC_TIMEOUT, SOC_USER, SOC_PASS
        server_proxy = SupervisorProxyFactory.create(SOC_URL, SOC_TIMEOUT, user=SOC_USER, password=SOC_PASS)
        return ProcessesManager(server_proxy)

    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    def _register_controllers(self):
        from .config import API_ENDPOINT, AUTH_URL
        from .controllers.health_controller import HealthController
        from .controllers.processes_controller import ProcessesController

        base_url_prefix = API_ENDPOINT

        self._service.register_blueprint(HealthController(base_url_prefix))
        self._service.register_blueprint(ProcessesController(
            base_url_prefix, AUTH_URL, self._processes_manager, service=self))