from __future__ import annotations

from datetime import datetime
import re
import subprocess
from typing import Any, Optional

from bluetooth_service.config import BT_ADAPTER_NAME, BT_SCAN_TIMEOUT
from bluetooth_service.exceptions.bluetooth_service_error import BluetoothServiceError
from bluetooth_service.models.bt_device import BtDevice


class BtDeviceManager:

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(self, adapter_name: str = BT_ADAPTER_NAME, scan_timeout: int = BT_SCAN_TIMEOUT) -> None:
        self._adapter_name = adapter_name
        self._scan_timeout = scan_timeout

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def find_nearby(self, timeout: Optional[int] = None) -> list[BtDevice]:
        timeout = timeout or self._scan_timeout

        try:
            devices = self._find_nearby_with_pybluez(timeout)
            if devices:
                return devices
        except BluetoothServiceError:
            pass

        self._run_bluetoothctl(['scan', 'on'], timeout=1, check=False)
        try:
            output = self._run_bluetoothctl(['devices'], timeout=timeout, check=False)
        finally:
            self._run_bluetoothctl(['scan', 'off'], timeout=1, check=False)

        return self._devices_from_bluetoothctl(output)

    def get_device_info(self, address: str) -> BtDevice:
        output = self._run_bluetoothctl(['info', address], timeout=5, check=False)
        if not output or 'Device ' not in output:
            raise BluetoothServiceError(f'Bluetooth device "{address}" was not found.')

        return self._device_from_info_output(address, output)

    def get_paired_devices(self) -> list[BtDevice]:
        output = self._run_bluetoothctl(['paired-devices'], timeout=5, check=False)
        devices = self._devices_from_bluetoothctl(output)
        result: list[BtDevice] = []
        for device in devices:
            try:
                result.append(self.get_device_info(device.address))
            except BluetoothServiceError:
                device.paired = True
                result.append(device)

        return result

    def pair_device(self, address: str, passkey: Optional[str] = None) -> BtDevice:
        command = f'pair {address}\ntrust {address}\nquit\n'
        if passkey:
            command = f'pair {address}\n{passkey}\ntrust {address}\nquit\n'
        self._run_bluetoothctl_script(command, timeout=30)
        return self.get_device_info(address)

    def unpair_device(self, address: str) -> bool:
        output = self._run_bluetoothctl(['remove', address], timeout=10, check=False)
        return 'Device has been removed' in output or 'not available' not in output

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    def _find_nearby_with_pybluez(self, timeout: int) -> list[BtDevice]:
        try:
            import bluetooth
        except ImportError as e:
            raise BluetoothServiceError('PyBluez "bluetooth" module is not installed.') from e

        try:
            rows = bluetooth.discover_devices(duration=timeout, lookup_names=True, flush_cache=True)
        except Exception as e:
            raise BluetoothServiceError(f'Failed to scan Bluetooth devices: {e}') from e

        return [
            BtDevice(address=str(address), name=name, alias=name, last_seen=datetime.now())
            for address, name in rows
        ]

    @staticmethod
    def _run_bluetoothctl(args: list[str], timeout: int = 10, check: bool = True) -> str:
        try:
            proc = subprocess.run(
                ['bluetoothctl', *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=timeout,
            )
        except FileNotFoundError as e:
            raise BluetoothServiceError('"bluetoothctl" command is not available.') from e
        except subprocess.TimeoutExpired as e:
            raise BluetoothServiceError(f'Bluetooth command timed out: bluetoothctl {" ".join(args)}') from e

        if check and proc.returncode != 0:
            raise BluetoothServiceError(proc.stderr.strip() or proc.stdout.strip() or 'Bluetooth command failed.')

        return proc.stdout

    @staticmethod
    def _run_bluetoothctl_script(script: str, timeout: int = 30) -> str:
        try:
            proc = subprocess.run(
                ['bluetoothctl'],
                input=script,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=timeout,
            )
        except FileNotFoundError as e:
            raise BluetoothServiceError('"bluetoothctl" command is not available.') from e
        except subprocess.TimeoutExpired as e:
            raise BluetoothServiceError('Bluetooth pairing command timed out.') from e

        if proc.returncode != 0:
            raise BluetoothServiceError(proc.stderr.strip() or proc.stdout.strip() or 'Bluetooth pairing command failed.')

        return proc.stdout

    def _devices_from_bluetoothctl(self, output: str) -> list[BtDevice]:
        devices: list[BtDevice] = []
        for line in output.splitlines():
            match = re.search(r'Device\s+([0-9A-Fa-f:]{17})\s*(.*)', line)
            if not match:
                continue
            devices.append(BtDevice(
                address=match.group(1).upper(),
                name=match.group(2).strip() or None,
                alias=match.group(2).strip() or None,
                last_seen=datetime.now(),
            ))

        return devices

    def _device_from_info_output(self, address: str, output: str) -> BtDevice:
        values: dict[str, Any] = {}
        for line in output.splitlines():
            if ':' not in line:
                continue
            key, value = line.strip().split(':', 1)
            values[key.strip().casefold()] = value.strip()

        return BtDevice(
            address=values.get('device', address).split()[0].upper(),
            name=values.get('name'),
            alias=values.get('alias'),
            paired=self._to_bool(values.get('paired')),
            trusted=self._to_bool(values.get('trusted')),
            connected=self._to_bool(values.get('connected')),
            blocked=self._to_bool(values.get('blocked')),
            rssi=self._to_int(values.get('rssi')),
            uuids=self._parse_uuids(output),
            last_seen=datetime.now(),
        )

    @staticmethod
    def _to_bool(value: Any) -> bool:
        return str(value).strip().casefold() == 'yes'

    @staticmethod
    def _to_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(str(value).strip())
        except ValueError:
            return None

    @staticmethod
    def _parse_uuids(output: str) -> list[str]:
        uuids: list[str] = []
        for line in output.splitlines():
            if 'UUID:' not in line:
                continue
            value = line.split('UUID:', 1)[1].strip()
            if value:
                uuids.append(value)

        return uuids
