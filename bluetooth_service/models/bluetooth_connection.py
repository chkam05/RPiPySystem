from datetime import datetime, time
import select
import threading
from typing import List, Optional

from bluetooth_service.exceptions.bluetooth_error import BluetoothError
from bluetooth_service.models.bluetooth_connection_info import BluetoothConnectionInfo
from bluetooth_service.models.bluetooth_message_record import BluetoothMessageRecord


class BluetoothConnection:
    """Represents a single Bluetooth RFCOMM connection."""

    def __init__(
        self,
        address: str,
        port: int,
        sock,
        name: Optional[str] = None,
        connection_id: Optional[str] = None,
    ):
        """
        Initialize connection with address, port, socket and metadata.
        """
        self.address = address
        self.port = port
        self.sock = sock

        if connection_id is None:
            connection_id = name or address

        self.info = BluetoothConnectionInfo(
            connection_id=connection_id,
            address=address,
            name=name,
            port=port,
        )

        # Incoming messages queue
        self._incoming: List[BluetoothMessageRecord] = []
        self._incoming_lock = threading.Lock()
        self._incoming_cv = threading.Condition(self._incoming_lock)

        # Listener thread
        self._stop_event = threading.Event()
        self._listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
        )
        self._listener_thread.start()

    # --------------------------------------------------------------------------
    # --- INTERNAL HELPER METHODS ---
    # --------------------------------------------------------------------------

    def _read_socket_once(self, bufsize: int = 1024, timeout: float = 0.5) -> Optional[bytes]:
        """
        Read from socket once with timeout, return None if nothing.
        """
        if not self.sock:
            raise BluetoothError('Socket is closed')
        ready, _, _ = select.select([self.sock], [], [], timeout)
        if ready:
            data = self.sock.recv(bufsize)
            if data:
                self.info.touch()
                return data
        return None
    
    def _listen_loop(self) -> None:
        """
        Background listener thread; pushes incoming data into queue.
        """
        while not self._stop_event.is_set():
            try:
                data = self._read_socket_once()
            except BluetoothError:
                break

            if not data:
                continue

            record = BluetoothMessageRecord(
                received_bytes=data,
                received_message=data.decode('utf-8', errors='ignore'),
                received_at=datetime.now(),
            )

            with self._incoming_cv:
                self._incoming.append(record)
                self._incoming_cv.notify_all()
    
    # --------------------------------------------------------------------------
    # --- PUBLIC METHODS ---
    # --------------------------------------------------------------------------

    def has_pending_messages(self) -> bool:
        """
        Return True if there are queued incoming messages.
        """
        with self._incoming_lock:
            return len(self._incoming) > 0
    
    def pending_count(self) -> int:
        """
        Return number of queued incoming messages.
        """
        with self._incoming_lock:
            return len(self._incoming)
    
    def send_msg(self, record: BluetoothMessageRecord) -> None:
        """
        Send message described by BluetoothMessageRecord.
        """
        if not self.sock:
            raise BluetoothError('Socket is closed.')

        payload: Optional[bytes] = None

        if record.send_message is not None:
            payload = record.send_message.encode('utf-8')
            record.send_bytes = payload
        elif record.send_bytes is not None:
            if isinstance(record.send_bytes, bytes):
                payload = record.send_bytes
            else:
                # If for some reason it were different.
                payload = bytes(record.send_bytes)
        else:
            raise ValueError('BluetoothMessageRecord has no send_message or send_bytes set.')
    
        record.send_at = datetime.now()
        self.sock.send(payload)
        self.info.touch()
    
    def receive_msg(self) -> Optional[BluetoothMessageRecord]:
        """
        Return next queued incoming message or None if queue is empty.
        """
        with self._incoming_lock:
            if not self._incoming:
                return None
            return self._incoming.pop(0)
    
    def send_receive_msg(self, record: BluetoothMessageRecord, read_timeout: int) -> BluetoothMessageRecord:
        """
        Send record and wait for first new incoming message after send.
        """
        # Remember how many messages were in read queue before sending.
        with self._incoming_lock:
            start_index = len(self._incoming)

        # Send message.
        self.send_msg(record)

        # Wait for incoming message.
        end_time = time.time() + read_timeout
        response_record: Optional[BluetoothMessageRecord] = None

        with self._incoming_cv:
            while time.time() < end_time:
                remaining = end_time - time.time()
                if remaining <= 0:
                    break

                if len(self._incoming) <= start_index:
                    self._incoming_cv.wait(timeout=remaining)

                if len(self._incoming) > start_index:
                    response_record = self._incoming.pop(start_index)
                    break

        if response_record is not None:
            record.received_message = response_record.received_message
            record.received_bytes = response_record.received_bytes
            record.received_at = response_record.received_at
        else:
            # timeout – nothing arrived after sending
            record.received_message = record.received_message or ''
            record.received_bytes = record.received_bytes or b''
            record.received_at = record.received_at or None

        return record

    def disconnect(self) -> None:
        """
        Close the connection and stop listener thread.
        """
        self._stop_event.set()
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None
        self.info.is_connected = False
        self.info.touch()