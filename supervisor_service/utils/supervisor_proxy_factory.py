import os
import xmlrpc.client
from urllib.parse import urlsplit, urlunsplit

from supervisor_service.config import SUPERVISOR_TIMEOUT, SUPERVISOR_URL, SUPERVISOR_USER, SUPERVISOR_PASS
from supervisor_service.utils.timeout_transport import TimeoutTransport


class SupervisorProxyFactory:
    
    @staticmethod
    def _inject_basic_auth(url: str, user: str | None, pwd: str | None) -> str:
        if not user or not pwd:
            return url
        parts = urlsplit(url)
        if "@" not in parts.netloc:
            netloc = f"{user}:{pwd}@{parts.hostname}"
            if parts.port:
                netloc += f":{parts.port}"
            parts = parts._replace(netloc=netloc)
        return urlunsplit(parts)

    @staticmethod
    def create(url: str, timeout: float = 3.0, user: str | None = None, pwd: str | None = None) -> xmlrpc.client.ServerProxy:
        """
        Creates a ServerProxy for:
          - unix:///path.sock   (uses supervisor.xmlrpc.SupervisorTransport)
          - hhttp(s)://.../RPC2 (HTTP + TimeoutTransport)
        """
        if url.startswith("unix://"):
            # Local import to avoid introducing dependencies when using only HTTP
            from supervisor.xmlrpc import SupervisorTransport
            transport = SupervisorTransport(username=None, password=None, serverurl=url)
            return xmlrpc.client.ServerProxy("http://127.0.0.1", transport=transport, allow_none=True)
        else:
            http_url = SupervisorProxyFactory._inject_basic_auth(url, user, pwd)
            transport = TimeoutTransport(timeout=timeout)
            return xmlrpc.client.ServerProxy(http_url, transport=transport, allow_none=True)

    @staticmethod
    def from_cofig() -> xmlrpc.client.ServerProxy:
        url = os.getenv("SUPERVISOR_URL", SUPERVISOR_URL)
        t = float(os.getenv("SUPERVISOR_TIMEOUT", SUPERVISOR_TIMEOUT))
        user = os.getenv("SUPERVISOR_USER", SUPERVISOR_USER)
        pwd = os.getenv("SUPERVISOR_PASS", SUPERVISOR_PASS)
        return SupervisorProxyFactory.create(url=url, timeout=t, user=user, pwd=pwd)
