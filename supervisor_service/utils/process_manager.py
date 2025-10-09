import socket
import xmlrpc.client

from .supervisor_proxy_factory import SupervisorProxyFactory


class ProcessManager:
    def __init__(self, server: xmlrpc.client.ServerProxy | None = None):
        self._server = server or SupervisorProxyFactory.from_cofig()
    
    # region --- Exception Wrapper ---

    @staticmethod
    def _wrap_call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (ConnectionRefusedError, TimeoutError, socket.gaierror, socket.timeout, OSError) as e:
            raise RuntimeError(f"supervisor xmlrpc unreachable: {e.__class__.__name__}") from e
        except xmlrpc.client.ProtocolError as e:
            raise RuntimeError(f"supervisor protocol error: {e.errcode} {e.errmsg}") from e
        except xmlrpc.client.Fault as e:
            raise RuntimeError(f"supervisor fault: {e.faultCode} {e.faultString}") from e

    # endregion --- Exception Wrapper ---
    
    def list_processes(self) -> list[dict]:
        data = self._wrap_call(self._server.supervisor.getAllProcessInfo)
        return [dict(p) for p in data]

    def start(self, name: str) -> dict:
        self._wrap_call(self._server.supervisor.startProcess, name)
        return self.info(name)

    def stop(self, name: str) -> dict:
        self._wrap_call(self._server.supervisor.stopProcess, name)
        return self.info(name)

    def restart(self, name: str) -> dict:
        self.stop(name)
        self.start(name)
        return self.info(name)

    def info(self, name: str) -> dict:
        return dict(self._wrap_call(self._server.supervisor.getProcessInfo, name))

    def stop_all(self) -> list[dict]:
        self._wrap_call(self._server.supervisor.stopAllProcesses)
        return self.list_processes()
