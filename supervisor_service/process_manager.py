import xmlrpc.client
from .config import SUPERVISOR_URL

class ProcessManager:
    def __init__(self, url: str | None = None):
        self._server = xmlrpc.client.ServerProxy(url or SUPERVISOR_URL)
    
    def list_processes(self) -> list[dict]:
        return [dict(p) for p in self._server.supervisor.getAllProcessInfo()]

    def start(self, name: str) -> dict:
        self._server.supervisor.startProcess(name)
        return self.info(name)

    def stop(self, name: str) -> dict:
        self._server.supervisor.stopProcess(name)
        return self.info(name)

    def restart(self, name: str) -> dict:
        self.stop(name)
        self.start(name)
        return self.info(name)

    def info(self, name: str) -> dict:
        return dict(self._server.supervisor.getProcessInfo(name))

    def stop_all(self) -> list[dict]:
        self._server.supervisor.stopAllProcesses()
        return self.list_processes()
