import xmlrpc


class SupervisorTimeoutTransport(xmlrpc.client.Transport):
    """HTTP transport for XML-RPC with socket timeout control."""
    
    def __init__(self, timeout: float = 3.0):
        """Initialize transport with a configurable socket timeout."""
        super().__init__()
        self._timeout = timeout

    def make_connection(self, host):
        """Create an HTTP connection and apply the configured timeout."""
        conn = super().make_connection(host)
        conn.timeout = self._timeout
        return conn