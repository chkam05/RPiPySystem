from __future__ import annotations

import http.client
from typing import Optional
from xmlrpc import client as xmlrpc_client


class SupervisorTimeoutTransport(xmlrpc_client.Transport):
    """HTTP XML-RPC transport with a socket timeout."""

    def __init__(self, timeout: float = 3.0, use_datetime: bool = False) -> None:
        super().__init__(use_datetime=use_datetime)
        self._timeout = timeout

    def make_connection(self, host: str) -> http.client.HTTPConnection:
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        connection = http.client.HTTPConnection(host, timeout=self._timeout)
        self._connection = host, connection
        return connection

    def close(self) -> None:
        connection: Optional[http.client.HTTPConnection] = None
        if self._connection:
            connection = self._connection[1]
        self._connection = None

        if connection:
            connection.close()
