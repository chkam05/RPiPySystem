from __future__ import annotations
from datetime import datetime, timedelta
import os

from core.system.models.process_info import ProcessInfo
from core.system.utilities._helpers import psutil


class ProcessesInfoUtility:
    ATTRS = ['pid', 'ppid', 'name', 'cmdline', 'username', 'uids', 'cpu_percent',
             'memory_percent', 'cpu_times', 'create_time', 'status', 'nice',
             'num_threads', 'terminal', 'memory_info']

    def get_processes(self) -> list[ProcessInfo]:
        if not psutil:
            return []

        processes: list[ProcessInfo] = []

        for process in psutil.process_iter(attrs=self.ATTRS):
            try:
                processes.append(self._process_from_info(process.info))
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                continue

        return processes

    def get_process_by_id(self, process_id: int) -> ProcessInfo | None:
        if not psutil:
            return None

        try:
            process = psutil.Process(process_id)
            return self._process_from_info(process.as_dict(attrs=self.ATTRS))
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            return None

    def _process_from_info(self, info: dict) -> ProcessInfo:
        cpu_times = info.get('cpu_times')
        memory_info = info.get('memory_info')
        uids = info.get('uids')
        create_time = info.get('create_time')

        return ProcessInfo(
            process_id=info.get('pid'),
            parent_process_id=info.get('ppid'),
            process_group_id=self._process_group_id(info.get('pid')),
            user_name=info.get('username'),
            user_id=getattr(uids, 'effective', None) if uids else None,
            real_user_id=getattr(uids, 'real', None) if uids else None,
            process_name=info.get('name'),
            command_line=' '.join(info.get('cmdline') or []),
            cpu_usage_percent=info.get('cpu_percent'),
            memory_usage_percent=info.get('memory_percent'),
            cpu_process_time=timedelta(seconds=(cpu_times.user + cpu_times.system)) if cpu_times else None,
            elapsed_since_start=timedelta(seconds=(datetime.now().timestamp() - create_time)) if create_time else None,
            started_at=datetime.fromtimestamp(create_time) if create_time else None,
            status=info.get('status'),
            terminal=info.get('terminal'),
            nice_value=info.get('nice'),
            virtual_memory_kb=int(memory_info.vms / 1024) if memory_info else None,
            resident_memory_kb=int(memory_info.rss / 1024) if memory_info else None,
            threads=info.get('num_threads'),
            major_page_faults=getattr(memory_info, 'pfaults', None) if memory_info else None,
        )

    def _process_group_id(self, pid: int | None) -> int | None:
        if pid is None:
            return None
        try:
            return os.getpgid(pid)
        except OSError:
            return None
