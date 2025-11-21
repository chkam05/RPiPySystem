from .utils.supervisor.supervisor_proc_manager import SupervisorProcManager
from .utils.supervisor.supervisor_proxy_factory import SupervisorProxyFactory
from utils.api.flask_api_service import FlaskApiService


class SystemService(FlaskApiService):

    def __init__(self):
        from .config import HOST, PORT, SERVICE_NAME

        self._supervisor_proc_manager = self._configure_supervisor_proc_manager()

        super().__init__(HOST, PORT, SERVICE_NAME)

    # --------------------------------------------------------------------------
    # --- CONFIGURATION METHODS ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _configure_supervisor_proc_manager() -> SupervisorProcManager:
        from .config import SOC_URL, SOC_TIMEOUT, SOC_USER, SOC_PASS
        server_proxy = SupervisorProxyFactory.create(SOC_URL, SOC_TIMEOUT, user=SOC_USER, password=SOC_PASS)
        return SupervisorProcManager(server_proxy)
    
    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    def _register_controllers(self):
        from .config import API_ENDPOINT, AUTH_URL
        from .controllers.health_controller import HealthController
        from .controllers.network_controller import NetworkController
        from .controllers.os_info_controller import OSInfoController
        from .controllers.os_usage_controller import OSUsageController
        from .controllers.supervisor_controller import SupervisorController
        # from .controllers.external_network_controller import ExternalNetworkController
        # from .controllers.internal_network_controller import InternalNetworkController
        # from .controllers.info_controller import InfoController
        # from .controllers.usage_controller import UsageController

        base_url_prefix = API_ENDPOINT

        HealthController(self, base_url_prefix)
        NetworkController(self, base_url_prefix, AUTH_URL)
        OSInfoController(self, base_url_prefix, AUTH_URL)
        OSUsageController(self, base_url_prefix, AUTH_URL)
        SupervisorController(self, base_url_prefix, AUTH_URL, self._supervisor_proc_manager)
        # self._service.register_blueprint(ExternalNetworkController(base_url_prefix, AUTH_URL))
        # self._service.register_blueprint(InternalNetworkController(base_url_prefix, AUTH_URL))
        # self._service.register_blueprint(InfoController(base_url_prefix, AUTH_URL))
        # self._service.register_blueprint(UsageController(base_url_prefix, AUTH_URL))
    
    def _register_error_handlers(self) -> None:
        """Register global error handlers for this service."""
        from flask import jsonify
        from .exceptions.supervisor_error import SupervisorError

        app = self.service

        @app.errorhandler(SupervisorError)
        def handle_supervisor_error(e: SupervisorError):
            return jsonify({
                "error": "SupervisorError",
                "message": str(e),
            }), 400