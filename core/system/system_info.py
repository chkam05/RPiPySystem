from __future__ import annotations

from core.system.models import (
    CPUInfo,
    CPUUsage,
    DiskUsage,
    ExternalNetworkInfo,
    InterfaceInfo,
    MemUsage,
    OSInfo,
    OSUsage,
    OSUserInfo,
    OSUserLoggedIn,
    ProcessInfo,
    TemperatureInfo,
)
from core.system.utilities import (
    CPUInfoUtility,
    DiskInfoUtility,
    MemInfoUtility,
    NetworkInfoUtility,
    OSInfoUtility,
    ProcessesInfoUtility,
    TempInfoUtility,
    UserInfoUtility,
)


class SystemInfo:
    def __init__(self) -> None:
        self.os = OSInfoUtility()
        self.cpu = CPUInfoUtility()
        self.disk = DiskInfoUtility()
        self.memory = MemInfoUtility()
        self.temperature = TempInfoUtility()
        self.users = UserInfoUtility()
        self.processes = ProcessesInfoUtility()
        self.network = NetworkInfoUtility()

    def get_os_info(self) -> OSInfo:
        return self.os.get_info()

    def get_cpu_info(self) -> CPUInfo:
        return self.cpu.get_info()

    def get_cpu_usage(self, interval: float = 0.1) -> CPUUsage:
        return self.cpu.get_usage(interval=interval)

    def get_disks(self, include_pseudo: bool = False) -> list[DiskUsage]:
        return self.disk.get_disks(include_pseudo=include_pseudo)

    def get_memory_usage(self) -> MemUsage:
        return self.memory.get_usage()

    def get_temperature_info(self) -> TemperatureInfo:
        return self.temperature.get_info()

    def get_users(self) -> list[OSUserInfo]:
        return self.users.get_users()

    def get_logged_in_users(self) -> list[OSUserLoggedIn]:
        return self.users.get_logged_in_users()

    def get_processes(self) -> list[ProcessInfo]:
        return self.processes.get_processes()

    def get_process_by_id(self, process_id: int) -> ProcessInfo | None:
        return self.processes.get_process_by_id(process_id)

    def get_network_interfaces(self) -> list[InterfaceInfo]:
        return self.network.get_interfaces()

    def get_network_interface(self, name: str) -> InterfaceInfo | None:
        return self.network.get_interface(name)

    def get_external_network_info(self) -> ExternalNetworkInfo | None:
        return self.network.get_external_info()

    def get_user_by_id_or_name(self, idname: str) -> OSUserInfo | None:
        return self.users.get_user_by_id_or_name(idname)

    def get_logged_in_user_by_name(self, name: str) -> OSUserLoggedIn | None:
        return self.users.get_logged_in_user_by_name(name)

    def get_logged_in_user_by_id_or_name(self, name: str) -> OSUserLoggedIn | None:
        return self.get_logged_in_user_by_name(name)

    def get_os_usage(self) -> OSUsage:
        return OSUsage(
            cpu=self.get_cpu_info(),
            cpu_usage=self.get_cpu_usage(),
            temperature=self.get_temperature_info(),
            memory=self.get_memory_usage(),
            disks=self.get_disks(),
        )
