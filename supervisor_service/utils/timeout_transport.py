import xmlrpc.client

class TimeoutTransport(xmlrpc.client.Transport):
    """
    HTTP transport for XML-RPC with socket timeout control.
    """
    
    def __init__(self, timeout: float = 3.0):
        super().__init__()
        self._timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self._timeout
        return conn
