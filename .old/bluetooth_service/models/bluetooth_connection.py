from collections import deque
from datetime import datetime
import select
import threading
import time
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
        self._last_sent = deque(maxlen=10)

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

    def _normalize_bytes(self, data: bytes) -> bytes:
        """
        Cuts off the final CR/LF, leaves the rest.
        """
        return data.rstrip(b'\r\n')

    def _normalize_text(self, text: str) -> str:
        return text.rstrip('\r\n')

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

            norm = self._normalize_bytes(data)
            if norm in self._last_sent:
                # Ignore echo.
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

    def _is_echo(self, sent: BluetoothMessageRecord, received: BluetoothMessageRecord) -> bool:
        if sent.send_bytes and received.received_bytes:
            if self._normalize_bytes(sent.send_bytes) == self._normalize_bytes(received.received_bytes):
                return True

        if sent.send_message and received.received_message:
            if self._normalize_text(sent.send_message) == self._normalize_text(received.received_message):
                return True

        return False

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
            payload = record.send_bytes if isinstance(record.send_bytes, bytes) else bytes(record.send_bytes)
        else:
            raise ValueError('BluetoothMessageRecord has no send_message or send_bytes set.')
    
        record.send_at = datetime.now()
        
        # Send.
        self.sock.send(payload)
        self.info.touch()

        # Remember payload for echo filtering.
        self._last_sent.append(self._normalize_bytes(payload))
    
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
        collected: List[BluetoothMessageRecord] = []

        with self._incoming_cv:
            while time.time() < end_time:
                remaining = end_time - time.time()
                if remaining <= 0:
                    break

                # If there are no new messages - wait.
                if len(self._incoming) <= start_index:
                    self._incoming_cv.wait(timeout=remaining)

                # After wake up – Get all new messages.
                while len(self._incoming) > start_index:
                    candidate = self._incoming.pop(start_index)

                    # Echo filter using normalized comparison
                    if self._is_echo(record, candidate):
                        continue

                    collected.append(candidate)

                # If something has already been received and the queue is empty, finish with rau.
                # Don't wait the entire timeout.
                if collected and len(self._incoming) <= start_index:
                    break

        if collected:
            # Concatenate text into a multi-line string.
            joined_message_parts = [
                c.received_message for c in collected if c.received_message is not None
            ]
            record.received_message = '\n'.join(joined_message_parts) if joined_message_parts else (record.received_message or '')

            # Concatenate bytes
            joined_bytes_parts = [
                c.received_bytes for c in collected if c.received_bytes is not None
            ]
            record.received_bytes = b''.join(joined_bytes_parts) if joined_bytes_parts else (record.received_bytes or b'')

            # Set receive time from last message.
            record.received_at = collected[-1].received_at
        else:
            # Timeout - nothing new arrived.
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