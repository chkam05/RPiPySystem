from typing import Optional
from urllib.parse import urlsplit, urlunsplit
from xmlrpc import client as xmlrpc_client

from .supervisor_timeout_transport import SupervisorTimeoutTransport


class SupervisorProxyFactory:
    """Factory for creating configured Supervisor XML-RPC proxies."""

    def __new__(cls, *args, **kwargs):
        """Prevent instantiation of this static utility class."""
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')

    @staticmethod
    def _inject_basic_auth(url: str, *, user: Optional[str] = None, password: Optional[str] = None) -> str:
        """Return URL with HTTP basic auth credentials injected if provided."""
        if not user or not password:
            return url
        parts = urlsplit(url)
        if "@" not in parts.netloc:
            netloc = f"{user}:{password}@{parts.hostname}"
            if parts.port:
                netloc += f":{parts.port}"
            parts = parts._replace(netloc=netloc)
        return urlunsplit(parts)
    
    @staticmethod
    def create(
        url: str,
        timeout: float = 3.0,
        *,
        user: Optional[str] = None,
        password: Optional[str] = None
    ) -> xmlrpc_client.ServerProxy:
        """Create and configure an XML-RPC ServerProxy for Supervisor."""
        if url.startswith("unix://"):
            # Local import to avoid introducing dependencies when using only HTTP
            from supervisor.xmlrpc import SupervisorTransport
            transport = SupervisorTransport(username=None, password=None, serverurl=url)
            return xmlrpc_client.ServerProxy("http://127.0.0.1", transport=transport, allow_none=True)
        else:
            http_url = SupervisorProxyFactory._inject_basic_auth(url, user=user, password=password)
            transport = SupervisorTimeoutTransport(timeout=timeout)
            return xmlrpc_client.ServerProxy(http_url, transport=transport, allow_none=True)