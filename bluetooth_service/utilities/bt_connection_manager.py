from __future__ import annotations

from typing import Optional

from bluetooth_service.config import BT_DEFAULT_RFCOMM_PORT, BT_READ_CHUNK_SIZE
from bluetooth_service.exceptions.bluetooth_service_error import BluetoothServiceError
from bluetooth_service.models.bt_connection_info import BtConnectionInfo
from bluetooth_service.utilities.bt_connection import BtConnection


class BtConnectionManager:

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(self, default_port: int = BT_DEFAULT_RFCOMM_PORT, read_chunk_size: int = BT_READ_CHUNK_SIZE) -> None:
        self._default_port = default_port
        self._read_chunk_size = read_chunk_size
        self._connections: dict[str, BtConnection] = {}

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def connect(
            self,
            address: str,
            port: Optional[int] = None,
            connection_id: Optional[str] = None,
            name: Optional[str] = None
        ) -> BtConnection:
        bt = self._import_bluetooth()
        port = port or self._default_port
        connection_id = connection_id or name or address

        if connection_id in self._connections and self._connections[connection_id].info.connected:
            return self._connections[connection_id]

        try:
            sock = bt.BluetoothSocket(bt.RFCOMM)
            sock.connect((address, port))
        except Exception as e:
            raise BluetoothServiceError(f'Failed to connect to Bluetooth device {address}: {e}') from e

        connection = BtConnection(connection_id, address, port, sock, name=name, read_chunk_size=self._read_chunk_size)
        self._connections[connection_id] = connection
        return connection

    def get_connection_list(self) -> list[BtConnectionInfo]:
        self._drop_closed()
        return [connection.to_info() for connection in self._connections.values()]

    def get_connection(self, connection_id: str) -> BtConnection | None:
        connection = self._connections.get(connection_id)
        if connection and connection.info.connected:
            return connection

        return None

    def disconnect(self, connection_id: str) -> bool:
        connection = self._connections.pop(connection_id, None)
        if not connection:
            return False

        connection.close()
        return True

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    def _drop_closed(self) -> None:
        for connection_id in list(self._connections.keys()):
            if not self._connections[connection_id].info.connected:
                self._connections.pop(connection_id, None)

    @staticmethod
    def _import_bluetooth():
        try:
            import bluetooth
            return bluetooth
        except ImportError as e:
            raise BluetoothServiceError('PyBluez "bluetooth" module is not installed.') from e
