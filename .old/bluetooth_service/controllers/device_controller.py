from typing import ClassVar, cast

from bluetooth_service.service import BluetoothService
from bluetooth_service.utils.bluetooth_manager import BluetoothManager
from utils.flask_api_service import FlaskApiService
from utils.mid_auth_controller import MidAuthController


class InfoController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'bluetooth_devices'
    _CONTROLLER_PATH: ClassVar[str] = 'devices'

    def __init__(self, url_prefix_base: str, auth_url: str, bt_manager: BluetoothManager) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        if not bt_manager:
            raise ValueError('bt_manager is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        self._bt_manager = bt_manager
        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> 'InfoController':
        self.add_url_rule('/', view_func=self.get_info, methods=['GET'])
        return self
    
    