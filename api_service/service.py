from core.api.flask_api_service import FlaskApiService
from core.supervisor.supervisor_connection import SupervisorConnection
from core.supervisor.supervisor_manager import SupervisorManager
from core.system.system_info import SystemInfo


class ApiService(FlaskApiService):

    def __init__(self):
        from .config import (
            HOST, PORT, SERVICE_NAME
        )

        self._supervisor_manager = self._configure_supervisor_manager()
        self._system_info = SystemInfo()

        super().__init__(HOST, PORT, SERVICE_NAME)

    # --------------------------------------------------------------------------------
    # CONFIGURATION METHODS
    # --------------------------------------------------------------------------------
    
    @staticmethod
    def _configure_supervisor_manager() -> SupervisorManager:
        from .config import (
            SERVICES_EXCLUDED_FROM_STOP, SUP_SOC_URL, SUP_SOC_TIMEOUT, SUP_SOC_USER, SUP_SOC_PASS
        )
        connection = SupervisorConnection.from_url(SUP_SOC_URL, SUP_SOC_TIMEOUT, user=SUP_SOC_USER, password=SUP_SOC_PASS)
        return SupervisorManager(connection, excluded_from_stop_all=SERVICES_EXCLUDED_FROM_STOP)

    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    def _register_controllers(self):
        from .config import ROUTE, AUTH_SERVICE_URL
        from .controllers.health_controller import HealthController
        from .controllers.supervisor_controller import SupervisorController
        from .controllers.network_controller import NetworkController
        from .controllers.system_controller import SystemController

        base_url_prefix = ROUTE

        HealthController(self, base_url_prefix)
        SupervisorController(self, self._supervisor_manager, AUTH_SERVICE_URL, base_url_prefix)
        NetworkController(self, self._system_info, AUTH_SERVICE_URL, base_url_prefix)
        SystemController(self, self._system_info, AUTH_SERVICE_URL, base_url_prefix)
