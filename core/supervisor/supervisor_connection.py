from __future__ import annotations
from typing import Any, Callable, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit
from xmlrpc import client as xmlrpc_client
import socket

from core.supervisor.enums.supervisor_action import SupervisorAction
from core.supervisor.enums.supervisor_process_state import SupervisorProcessState
from core.supervisor.exceptions.supervisor_error import SupervisorError
from core.supervisor.supervisor_timeout_transport import SupervisorTimeoutTransport


ServerProxyFactory = Callable[[], xmlrpc_client.ServerProxy]


class SupervisorConnection:
    """Middleware responsible for Supervisor XML-RPC connection handling."""

    _CONNECTION_ERRORS = (
        ConnectionRefusedError,
        TimeoutError,
        socket.gaierror,
        socket.timeout,
        OSError,
    )

    def __init__(
        self,
        server_proxy: Optional[xmlrpc_client.ServerProxy] = None,
        *,
        proxy_factory: Optional[ServerProxyFactory] = None,
        reconnect_attempts: int = 1,
    ) -> None:
        if server_proxy is None and proxy_factory is None:
            raise ValueError('SupervisorConnection requires server_proxy or proxy_factory.')

        self._server_proxy = server_proxy
        self._proxy_factory = proxy_factory
        self._reconnect_attempts = max(0, int(reconnect_attempts))

    @classmethod
    def from_url(
        cls,
        url: str,
        timeout: float = 3.0,
        *,
        user: Optional[str] = None,
        password: Optional[str] = None,
        reconnect_attempts: int = 1,
    ) -> SupervisorConnection:
        """Create a reconnectable Supervisor connection from an HTTP or unix URL."""
        return cls(
            proxy_factory=lambda: cls._create_server_proxy(
                url,
                timeout=timeout,
                user=user,
                password=password,
            ),
            reconnect_attempts=reconnect_attempts,
        )

    # --------------------------------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------------------------------

    @property
    def server_proxy(self) -> xmlrpc_client.ServerProxy:
        if self._server_proxy is None:
            self.reconnect()
        return self._server_proxy
    
    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    @staticmethod
    def action_success(action: SupervisorAction, info: dict[str, Any]) -> Tuple[bool, str]:
        """Determine if a Supervisor process action succeeded based on process info."""
        name = info.get('name')
        state_name = str(info.get('statename') or '').upper()

        if action in (SupervisorAction.START, SupervisorAction.RESTART):
            ok = state_name in SupervisorProcessState.start_success_states()
            return ok, f'{name} state={state_name}'

        if action == SupervisorAction.STOP:
            ok = state_name in SupervisorProcessState.stop_success_states()
            return ok, f'{name} state={state_name}'

        return False, f'{name} unknown action'

    def call(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call an XML-RPC function, reconnecting once on transport failures."""
        try_count = self._reconnect_attempts + 1
        
        for attempt in range(try_count):
            try:
                return fn(*args, **kwargs)
            except self._CONNECTION_ERRORS as e:
                if attempt >= self._reconnect_attempts:
                    raise SupervisorError(f'Supervisor xmlrpc unreachable: {e.__class__.__name__}') from e
                self.reconnect()
                fn = self._refresh_bound_method(fn)
            except xmlrpc_client.ProtocolError as e:
                raise SupervisorError(f'Supervisor protocol error: {e.errcode} {e.errmsg}') from e
            except xmlrpc_client.Fault as e:
                raise SupervisorError(f'Supervisor fault: {e.faultCode} {e.faultString}') from e

        raise SupervisorError('Supervisor xmlrpc unreachable.')

    def close(self) -> None:
        """Close a cached transport connection if the underlying transport supports it."""
        transport = getattr(self._server_proxy, '_ServerProxy__transport', None)

        if transport and hasattr(transport, 'close'):
            transport.close()
        self._server_proxy = None if self._proxy_factory else self._server_proxy

    def supervisor_call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        """Call a method from the Supervisor XML-RPC namespace."""
        fn = getattr(self.server_proxy.supervisor, method)
        return self.call(fn, *args, **kwargs)

    def reconnect(self) -> None:
        """Drop the current XML-RPC proxy connection and create a new one if possible."""
        self.close()

        if self._proxy_factory is None:
            return
        self._server_proxy = self._proxy_factory()

    # --------------------------------------------------------------------------------
    # UTILITIES
    # --------------------------------------------------------------------------------

    @staticmethod
    def _create_server_proxy(
        url: str,
        timeout: float = 3.0,
        *,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> xmlrpc_client.ServerProxy:
        if url.startswith('unix://'):
            from supervisor.xmlrpc import SupervisorTransport

            transport = SupervisorTransport(username=user, password=password, serverurl=url)
            return xmlrpc_client.ServerProxy('http://127.0.0.1', transport=transport, allow_none=True)

        http_url = SupervisorConnection._inject_basic_auth(url, user=user, password=password)
        transport = SupervisorTimeoutTransport(timeout=timeout)
        return xmlrpc_client.ServerProxy(http_url, transport=transport, allow_none=True)

    @staticmethod
    def _inject_basic_auth(url: str, *, user: Optional[str] = None, password: Optional[str] = None) -> str:
        if not user or not password:
            return url

        parts = urlsplit(url)
        if '@' in parts.netloc:
            return url

        netloc = f'{user}:{password}@{parts.hostname}'
        if parts.port:
            netloc += f':{parts.port}'

        return urlunsplit(parts._replace(netloc=netloc))

    def _refresh_bound_method(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        method_name = getattr(fn, '_Method__name', None)
        if not method_name:
            return fn

        refreshed: Any = self.server_proxy
        for part in str(method_name).split('.'):
            refreshed = getattr(refreshed, part)
        return refreshed
