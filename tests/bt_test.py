import sys
from pathlib import Path
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


class BTLiveTests(SimpleTestCase):

    def config(self) -> None:
        self.bt_manager = BluetoothManager()
        self.hc_06: Optional[BluetoothDeviceInfo] = None
        self.connection: Optional[BluetoothConnection] = None

    @testcase
    def test_01_enabled(self) -> None:
        if not self.bt_manager.is_enabled():
            self.bt_manager.enable_bt()
            if not self.bt_manager.is_enabled():
                self.fail('Could not enable bluetooth module.')

    @testcase
    def test_02_scan(self) -> None:
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

                if device.name == 'HC-06':
                    self.hc_06 = device
                
        except Exception as e:
            self.fail(str(e))
    
    @testcase
    def test_03_pair(self) -> None:
        self.is_not_null(self.hc_06)
        self.is_instance_of_type(self.hc_06, BluetoothDeviceInfo)

        dev_address = self.hc_06.address

        try:
            if not self.bt_manager.is_paired(dev_address):
                self.bt_manager.pair(dev_address, '1234')
                if not self.bt_manager.is_paired(dev_address):
                    self.fail(f'Could not pair device \"{self.hc_06.name}\".')
        except BluetoothAuthenticationError as bae:
            self.fail(str(bae))
            raise
        except BluetoothError as be:
            self.fail(str(be))
            raise
        except Exception as e:
            self.fail(str(e))
            raise
        
        try:
            if not self.bt_manager.is_connected(dev_address):
                connection = self.bt_manager.connect(dev_address)
                self.is_not_null(connection)
                self.is_instance_of_type(connection, BluetoothConnection)
        except BluetoothError as be:
            self.fail(str(be))
            raise
        except Exception as e:
            self.fail(str(e))
            raise
    
    @testcase
    def test_04_msg(self) -> None:
        self.is_not_null(self.connection)
        self.is_instance_of_type(self.connection, BluetoothConnection)

        self.connection.send_msg(BluetoothMessageRecord('/msg Hello World'))

if __name__ == '__main__':
    BTLiveTests().run()