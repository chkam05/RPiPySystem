from flask import jsonify

from bluetooth_service.exceptions.bluetooth_service_error import BluetoothServiceError
from bluetooth_service.utilities.bt_connection_manager import BtConnectionManager
from bluetooth_service.utilities.bt_device_manager import BtDeviceManager
from core.api.flask_api_service import FlaskApiService
from core.data.error_response import ErrorResponse


class BluetoothService(FlaskApiService):

    def __init__(self):
        from .config import HOST, PORT, SERVICE_NAME

        self._device_manager = BtDeviceManager()
        self._connection_manager = BtConnectionManager()

        super().__init__(HOST, PORT, SERVICE_NAME)

    # --------------------------------------------------------------------------------
    # CONFIGURATION METHODS
    # --------------------------------------------------------------------------------

    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE
        return super()._configure_swagger(template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

    def _register_controllers(self):
        from .config import AUTH_SERVICE_URL, ROUTE
        from .controllers.connections_controller import ConnectionsController
        from .controllers.devices_controller import DevicesController

        DevicesController(self, self._device_manager, AUTH_SERVICE_URL, ROUTE)
        ConnectionsController(self, self._connection_manager, AUTH_SERVICE_URL, ROUTE)

    def _register_error_handlers(self) -> None:
        app = self.service

        @app.errorhandler(BluetoothServiceError)
        def handle_bluetooth_service_error(e: BluetoothServiceError):
            return jsonify(ErrorResponse(
                message='Bluetooth service error.',
                code=400,
                details=str(e),
            ).to_public()), 400

        @app.errorhandler(KeyError)
        def handle_key_error(e: KeyError):
            return jsonify(ErrorResponse(
                message='Bad request.',
                code=400,
                details=f'Missing required field: {e}',
            ).to_public()), 400
