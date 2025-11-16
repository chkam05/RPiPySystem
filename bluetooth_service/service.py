from bluetooth_service.utils.bluetooth_manager import BluetoothManager
from utils.flask_api_service import FlaskApiService


class BluetoothService(FlaskApiService):

    def __init__(self):
        from .config import HOST, PORT, SERVICE_NAME

        self.bt_manager = BluetoothManager()
        
        super().__init__(HOST, PORT, SERVICE_NAME)

    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    def _register_controllers(self):
        from .config import API_ENDPOINT, AUTH_URL
        from .controllers.health_controller import HealthController

        base_url_prefix = API_ENDPOINT

        self._service.register_blueprint(HealthController(base_url_prefix))