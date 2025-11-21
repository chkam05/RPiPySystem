import sys
from pathlib import Path
import time
from typing import Optional

from bluetooth_service.exceptions.bluetooth_authentication_error import BluetoothAuthenticationError
from bluetooth_service.exceptions.bluetooth_error import BluetoothError
from bluetooth_service.models.bluetooth_message_record import BluetoothMessageRecord

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bluetooth_service.models.bluetooth_connection import BluetoothConnection
from bluetooth_service.models.bluetooth_device_info import BluetoothDeviceInfo
from bluetooth_service.utils.bluetooth_manager import BluetoothManager
from tests.common.test_framework import SimpleTestCase, testcase


class TestBtManager(SimpleTestCase):

    def config(self) -> None:
        self.device_name = 'HC-06'
        self.bt_manager = BluetoothManager()
        self.device: Optional[BluetoothDeviceInfo] = None
        self.connection: Optional[BluetoothConnection] = None

    @testcase
    def test_01_is_enabled(self) -> None:
        if not self.bt_manager.is_enabled():
            self.bt_manager.enable_bt()
            if not self.bt_manager.is_enabled():
                self.fail('Could not enable bluetooth module.')
    
    @testcase
    def test_02_scan_devices(self) -> None:
        try:
            scan_devices = self.bt_manager.scan()

            for device in scan_devices:
                self.is_instance_of_type(device, BluetoothDeviceInfo)
                device: BluetoothDeviceInfo

                print(f'    {device.address}: {device.name}')
                self.is_not_empty(device.address)
                device = self.bt_manager.get_device_info(device.address)
                self.is_instance_of_type(device, BluetoothDeviceInfo)
                self.is_not_empty(device.alias)

                if device.name == self.device_name:
                    self.device = device
                
        except BluetoothAuthenticationError as bae:
            self.fail(f'BluetoothAuthenticationError: {str(bae)}')
        except BluetoothError as be:
            self.fail(f'BluetoothError: {str(be)}')
        except Exception as e:
            self.fail(f'Exception: {str(e)}')
    
    @testcase
    def test_03_pair_device(self) -> None:
        self.is_not_null(self.device)
        self.is_instance_of_type(self.device, BluetoothDeviceInfo)

        try:
            if not self.bt_manager.is_paired(self.device.address):
                self.bt_manager.pair(self.device.address, '1234')
                if not self.bt_manager.is_paired(self.device.address):
                    self.fail(f'Could not pair device \"{self.device.name}\".')
            
        except BluetoothAuthenticationError as bae:
            self.fail(f'BluetoothAuthenticationError: {str(bae)}')
        except BluetoothError as be:
            self.fail(f'BluetoothError: {str(be)}')
        except Exception as e:
            self.fail(f'Exception: {str(e)}')
    
    @testcase
    def test_04_connect_to_device(self) -> None:
        self.is_not_null(self.device)
        self.is_instance_of_type(self.device, BluetoothDeviceInfo)
        
        try:
            if not self.bt_manager.is_connected(self.device.address):
                connection = self.bt_manager.connect(self.device.address)
                self.is_not_null(connection)
                self.is_instance_of_type(connection, BluetoothConnection)
                self.connection = connection
        
        except BluetoothAuthenticationError as bae:
            self.fail(f'BluetoothAuthenticationError: {str(bae)}')
        except BluetoothError as be:
            self.fail(f'BluetoothError: {str(be)}')
        except Exception as e:
            self.fail(f'Exception: {str(e)}')
    
    @testcase
    def test_05_send_receive_message(self) -> None:
        self.is_not_null(self.connection)
        self.is_instance_of_type(self.connection, BluetoothConnection)

        try:
            response = self.connection.send_receive_msg(BluetoothMessageRecord('/msg test'), 10)
            self.is_not_null(response)
            self.is_instance_of_type(response, BluetoothMessageRecord)
            self.contains(response.received_message, "OK")
        
        except BluetoothAuthenticationError as bae:
            self.fail(f'BluetoothAuthenticationError: {str(bae)}')
        except BluetoothError as be:
            self.fail(f'BluetoothError: {str(be)}')
        except Exception as e:
            self.fail(f'Exception: {str(e)}')

if __name__ == '__main__':
    TestBtManager().run()