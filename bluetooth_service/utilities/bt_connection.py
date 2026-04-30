from __future__ import annotations

from collections import deque
from datetime import datetime
import select
import threading
import time
from typing import Optional

from bluetooth_service.exceptions.bluetooth_service_error import BluetoothServiceError
from bluetooth_service.models.bt_connection_info import BtConnectionInfo
from bluetooth_service.models.bt_message import BtMessage
from bluetooth_service.models.bt_message_pair import BtMessagePair


class BtConnection:

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(
            self,
            connection_id: str,
            address: str,
            port: int,
            sock,
            name: Optional[str] = None,
            read_chunk_size: int = 1024
        ) -> None:
        self._sock = sock
        self._read_chunk_size = read_chunk_size
        self._received: deque[BtMessage] = deque()
        self._last_sent: deque[bytes] = deque(maxlen=10)
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._stop_event = threading.Event()
        self._direct_waiting = False
        self._direct_chunks: list[bytes] = []
        self._buffer = b''
        self._buffer_updated_at: Optional[float] = None

        self.info = BtConnectionInfo(
            connection_id=connection_id,
            address=address,
            name=name,
            port=port,
            connected=True,
        )

        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def close(self) -> None:
        self._stop_event.set()
        self.info.connected = False
        try:
            self._sock.close()
        except Exception:
            pass

    def send_message(self, message: BtMessage) -> BtMessage:
        payload = message.payload()
        if not payload:
            raise BluetoothServiceError('Message payload is empty.')

        self._send_payload(payload)
        return BtMessage(message=message.message, bytes=payload, issued_at=datetime.now(), from_device='service')

    def receive_message(self) -> Optional[BtMessage]:
        with self._condition:
            if not self._received:
                return None
            return self._received.popleft()

    def send_and_receive(self, message: BtMessage, timeout: float = 5.0) -> BtMessagePair:
        payload = message.payload()
        if not payload:
            raise BluetoothServiceError('Message payload is empty.')

        sent = BtMessage(message=message.message, bytes=payload, issued_at=datetime.now(), from_device='service')
        with self._condition:
            self._direct_waiting = True
            self._direct_chunks = []

        self._send_payload(payload)
        deadline = time.time() + max(0.0, timeout)
        received: Optional[BtMessage] = None

        with self._condition:
            while time.time() < deadline:
                remaining = deadline - time.time()
                if remaining <= 0:
                    break
                if not self._direct_chunks:
                    self._condition.wait(timeout=remaining)
                    continue

                current_count = len(self._direct_chunks)
                self._condition.wait(timeout=min(0.2, max(0.0, deadline - time.time())))
                if len(self._direct_chunks) > current_count:
                    continue

                data = b''.join(self._direct_chunks)
                if self._is_echo(data):
                    self._direct_chunks = []
                    continue

                received = self._message_from_bytes(data)
                break

            self._direct_waiting = False
            self._direct_chunks = []

        return BtMessagePair(send=sent, received=received)

    def get_received_count(self) -> int:
        with self._condition:
            return len(self._received)

    def get_received_list(self) -> list[BtMessage]:
        with self._condition:
            items = list(self._received)
            self._received.clear()
            return items

    def to_info(self) -> BtConnectionInfo:
        self.info.received_count = self.get_received_count()
        return self.info

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    def _send_payload(self, payload: bytes) -> None:
        if not self.info.connected:
            raise BluetoothServiceError('Connection is closed.')

        try:
            self._sock.send(payload)
        except Exception as e:
            self.info.connected = False
            raise BluetoothServiceError(f'Failed to send Bluetooth message: {e}') from e

        self.info.touch()
        self._last_sent.append(self._normalize_payload(payload))

    def _listen_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                ready, _, _ = select.select([self._sock], [], [], 0.2)
                if not ready:
                    self._flush_idle_buffer()
                    continue
                data = self._sock.recv(self._read_chunk_size)
            except Exception:
                break

            if not data:
                continue

            self.info.touch()
            if self._is_echo(data):
                continue

            with self._condition:
                if self._direct_waiting:
                    self._direct_chunks.append(data)
                    self._condition.notify_all()
                    continue

                for message in self._split_messages(data):
                    self._received.append(message)
                self._condition.notify_all()

        self.info.connected = False

    def _split_messages(self, data: bytes) -> list[BtMessage]:
        self._buffer += data
        self._buffer_updated_at = time.time()

        return []

    def _flush_idle_buffer(self) -> None:
        with self._condition:
            if not self._buffer or self._buffer_updated_at is None:
                return
            if time.time() - self._buffer_updated_at < 0.2:
                return

            data = self._buffer.rstrip(b'\r\n')
            self._buffer = b''
            self._buffer_updated_at = None
            if data:
                self._received.append(self._message_from_bytes(data))
                self._condition.notify_all()

    def _message_from_bytes(self, data: bytes) -> BtMessage:
        return BtMessage(
            message=data.decode('utf-8', errors='ignore'),
            bytes=data,
            issued_at=datetime.now(),
            from_device=self.info.address,
        )

    @staticmethod
    def _normalize_payload(payload: bytes) -> bytes:
        return payload.rstrip(b'\r\n')

    def _is_echo(self, data: bytes) -> bool:
        normalized = self._normalize_payload(data)
        return any(normalized == sent for sent in self._last_sent)
