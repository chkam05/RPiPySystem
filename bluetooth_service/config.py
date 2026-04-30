from typing import Optional
import os


# SERVICE CONFIGURATION

HOST = os.getenv('BLUETOOTH_SERVICE_HOST')
PORT = int(os.getenv('BLUETOOTH_SERVICE_PORT'))
ROUTE = os.getenv('BLUETOOTH_SERVICE_ROUTE')
SERVICE_NAME = 'bluetooth_service'
SWAGGER_DESCRIPTION = 'Bluetooth device and RFCOMM communication service.\n'
SWAGGER_TITLE = 'Bluetooth Service API'

# AUTHENTICATION

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL')

# BLUETOOTH

BT_ADAPTER_NAME = os.getenv('BLUETOOTH_ADAPTER_NAME', 'hci0')
BT_SCAN_TIMEOUT = int(os.getenv('BLUETOOTH_SCAN_TIMEOUT', '8'))
BT_DEFAULT_RFCOMM_PORT = int(os.getenv('BLUETOOTH_DEFAULT_RFCOMM_PORT', '1'))
BT_READ_CHUNK_SIZE = int(os.getenv('BLUETOOTH_READ_CHUNK_SIZE', '1024'))


def require_config() -> Optional[str]:
    missing = [
        name for name, value in {
            'BLUETOOTH_SERVICE_HOST': HOST,
            'BLUETOOTH_SERVICE_PORT': PORT,
            'BLUETOOTH_SERVICE_ROUTE': ROUTE,
            'AUTH_SERVICE_URL': AUTH_SERVICE_URL,
        }.items()
        if value is None or value == ''
    ]
    return ', '.join(missing) if missing else None
