from __future__ import annotations

import json
import os
import socket
import threading
from typing import Callable

from io_service.models.io_command import IOCommand
from io_service.models.io_response import IOResponse


CommandHandler = Callable[[IOCommand], IOResponse]


class InternalServer:

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(self, socket_path: str, handler: CommandHandler) -> None:
        self._socket_path = socket_path
        self._handler = handler
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def start(self) -> None:
        socket_dir = os.path.dirname(os.path.abspath(self._socket_path))
        if socket_dir:
            os.makedirs(socket_dir, exist_ok=True)
        if os.path.exists(self._socket_path):
            os.unlink(self._socket_path)

        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(self._socket_path)
        self._sock.listen(8)

        self._thread = threading.Thread(target=self._serve_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
        if os.path.exists(self._socket_path):
            os.unlink(self._socket_path)

    @staticmethod
    def request(socket_path: str, command: IOCommand, timeout: float = 5.0) -> IOResponse:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            client.connect(socket_path)
            client.sendall(json.dumps(command.to_dict()).encode('utf-8') + b'\n')
            raw = InternalServer._read_line(client)
        return IOResponse.from_dict(json.loads(raw.decode('utf-8')))

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    def _serve_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                client, _ = self._sock.accept()
            except OSError:
                break
            threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()

    def _handle_client(self, client: socket.socket) -> None:
        with client:
            try:
                raw = self._read_line(client)
                command = IOCommand.from_dict(json.loads(raw.decode('utf-8')))
                response = self._handler(command)
            except Exception as e:
                response = IOResponse(ok=False, error=str(e))

            client.sendall(json.dumps(response.to_dict()).encode('utf-8') + b'\n')

    @staticmethod
    def _read_line(sock: socket.socket) -> bytes:
        chunks: list[bytes] = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if b'\n' in chunk:
                break

        data = b''.join(chunks)
        return data.split(b'\n', 1)[0]
