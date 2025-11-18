from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar, Dict, List, Optional


@dataclass
class ProcessInfo:
    # --- Field-name constants ---
    FIELD_PROCESS_ID: ClassVar[str] = 'process_id'
    FIELD_PARENT_PROCESS_ID: ClassVar[str] = 'parent_process_id'
    FIELD_PROCESS_GROUP_ID: ClassVar[str] = 'process_group_id'
    FIELD_USER_NAME: ClassVar[str] = 'user_name'
    FIELD_USER_ID: ClassVar[str] = 'user_id'
    FIELD_REAL_USER_NAME: ClassVar[str] = 'real_user_name'
    FIELD_REAL_USER_ID: ClassVar[str] = 'real_user_id'
    FIELD_PROCESS_NAME: ClassVar[str] = 'process_name'
    FIELD_COMMAND_LINE: ClassVar[str] = 'command_line'
    FIELD_CPU_USAGE_PERCENT: ClassVar[str] = 'cpu_usage_percent'
    FIELD_MEMORY_USAGE_PERCENT: ClassVar[str] = 'memory_usage_percent'
    FIELD_CPU_PROCESS_TIME: ClassVar[str] = 'cpu_process_time'
    FIELD_ELAPSED_SINCE_START: ClassVar[str] = 'elapsed_since_start'
    FIELD_STARTED_AT: ClassVar[str] = 'started_at'
    FIELD_STATUS: ClassVar[str] = 'status'
    FIELD_TERMINAL: ClassVar[str] = 'terminal'
    FIELD_PRIORITY: ClassVar[str] = 'priority'
    FIELD_NICE_VALUE: ClassVar[str] = 'nice_value'
    FIELD_SCHEDULER_CLASS: ClassVar[str] = 'scheduler_class'
    FIELD_SCHEDULER_POLICY: ClassVar[str] = 'scheduler_policy'
    FIELD_REALTIME_PRIORITY: ClassVar[str] = 'realtime_priority'
    FIELD_VIRTUAL_MEMORY_KB: ClassVar[str] = 'virtual_memory_kb'
    FIELD_RESIDENT_MEMORY_KB: ClassVar[str] = 'resident_memory_kb'
    FIELD_CURRENT_CPU: ClassVar[str] = 'current_cpu'
    FIELD_CGROUP_PATH: ClassVar[str] = 'cgroup_path'
    FIELD_THREADS: ClassVar[str] = 'threads'
    FIELD_WAIT_CHANNEL: ClassVar[str] = 'wait_channel'
    FIELD_KERNEL_FLAGS: ClassVar[str] = 'kernel_flags'
    FIELD_MAJOR_PAGE_FAULTS: ClassVar[str] = 'major_page_faults'
    FIELD_MINOR_PAGE_FAULTS: ClassVar[str] = 'minor_page_faults'
    FIELD_SESSION_ID: ClassVar[str] = 'session_id'
    FIELD_THREAD_GROUP_ID: ClassVar[str] = 'thread_group_id'

    # --- Fields ---
    process_id: Optional[int]
    parent_process_id: Optional[int]
    process_group_id: Optional[int]

    user_name: Optional[str]                    # effective user
    user_id: Optional[int]                      # effective uid
    real_user_name: Optional[str]               # ruser
    real_user_id: Optional[int]                 # ruid

    process_name: Optional[str]                 # comm
    command_line: Optional[str]                 # args/cmd

    cpu_usage_percent: Optional[float]          # %CPU
    memory_usage_percent: Optional[float]       # %MEM
    cpu_process_time: Optional[timedelta]       # timedelta
    elapsed_since_start: Optional[timedelta]    # timedelta
    started_at: Optional[datetime]              # datetime

    status: Optional[str]                       # stat (full)
    terminal: Optional[str]                     # tty

    priority: Optional[int]                     # pri
    nice_value: Optional[int]                   # nice
    scheduler_class: Optional[str]              # cls
    scheduler_policy: Optional[str]             # policy
    realtime_priority: Optional[str]            # rtprio

    virtual_memory_kb: Optional[int]            # vsz
    resident_memory_kb: Optional[int]           # rss

    current_cpu: Optional[int]                  # psr
    cgroup_path: Optional[str]                  # cgroup
    threads: Optional[int]                      # nlwp
    wait_channel: Optional[str]                 # wchan

    kernel_flags: Optional[str]                 # flags/f

    major_page_faults: Optional[int]            # maj_flt
    minor_page_faults: Optional[int]            # min_flt

    session_id: Optional[int]                   # sid
    thread_group_id: Optional[int]              # tgid

    # --- Packaging methods ---

    @staticmethod
    def _parse_datetime_str(v: Any) -> Optional[datetime]:
        if isinstance(v, datetime):
            return v
        if v is None:
            return None
        s = str(v).strip()
        if not s or s == '-':
            return None
        # try new format first
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y.%m.%d-%H:%M:%S'):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    @staticmethod
    def _parse_timedelta_str(v: Any) -> Optional[timedelta]:
        if isinstance(v, timedelta):
            return v
        if v is None:
            return None
        s = str(v).strip()
        if not s or s == '-':
            return None

        days = 0
        time_part = s
        if '-' in s:
            d, time_part = s.split('-', 1)
            try:
                days = int(d)
            except ValueError:
                return None

        parts = time_part.split(':')
        try:
            if len(parts) == 3:
                h, m, sec = [int(p) for p in parts]
            elif len(parts) == 2:
                h, m, sec = 0, int(parts[0]), int(parts[1])
            else:
                return None
        except ValueError:
            return None

        return timedelta(days=days, hours=h, minutes=m, seconds=sec)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ProcessInfo':
        return cls(
            process_id=d.get(cls.FIELD_PROCESS_ID),
            parent_process_id=d.get(cls.FIELD_PARENT_PROCESS_ID),
            process_group_id=d.get(cls.FIELD_PROCESS_GROUP_ID),
            user_name=d.get(cls.FIELD_USER_NAME),
            user_id=d.get(cls.FIELD_USER_ID),
            real_user_name=d.get(cls.FIELD_REAL_USER_NAME),
            real_user_id=d.get(cls.FIELD_REAL_USER_ID),
            process_name=d.get(cls.FIELD_PROCESS_NAME),
            command_line=d.get(cls.FIELD_COMMAND_LINE),
            cpu_usage_percent=d.get(cls.FIELD_CPU_USAGE_PERCENT),
            memory_usage_percent=d.get(cls.FIELD_MEMORY_USAGE_PERCENT),
            cpu_process_time=cls._parse_timedelta_str(d.get(cls.FIELD_CPU_PROCESS_TIME)),
            elapsed_since_start=cls._parse_timedelta_str(d.get(cls.FIELD_ELAPSED_SINCE_START)),
            started_at=cls._parse_datetime_str(d.get(cls.FIELD_STARTED_AT)),
            status=d.get(cls.FIELD_STATUS),
            terminal=d.get(cls.FIELD_TERMINAL),
            priority=d.get(cls.FIELD_PRIORITY),
            nice_value=d.get(cls.FIELD_NICE_VALUE),
            scheduler_class=d.get(cls.FIELD_SCHEDULER_CLASS),
            scheduler_policy=d.get(cls.FIELD_SCHEDULER_POLICY),
            realtime_priority=d.get(cls.FIELD_REALTIME_PRIORITY),
            virtual_memory_kb=d.get(cls.FIELD_VIRTUAL_MEMORY_KB),
            resident_memory_kb=d.get(cls.FIELD_RESIDENT_MEMORY_KB),
            current_cpu=d.get(cls.FIELD_CURRENT_CPU),
            cgroup_path=d.get(cls.FIELD_CGROUP_PATH),
            threads=d.get(cls.FIELD_THREADS),
            wait_channel=d.get(cls.FIELD_WAIT_CHANNEL),
            kernel_flags=d.get(cls.FIELD_KERNEL_FLAGS),
            major_page_faults=d.get(cls.FIELD_MAJOR_PAGE_FAULTS),
            minor_page_faults=d.get(cls.FIELD_MINOR_PAGE_FAULTS),
            session_id=d.get(cls.FIELD_SESSION_ID),
            thread_group_id=d.get(cls.FIELD_THREAD_GROUP_ID),
        )
    
    def _fmt_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        return dt.strftime('%Y-%m-%d %H:%M:%S') if isinstance(dt, datetime) else None
    
    def _fmt_timedelta(self, td: Optional[timedelta]) -> Optional[str]:
        if not isinstance(td, timedelta):
            return None
        total = int(td.total_seconds())
        days, rem = divmod(total, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        if days:
            return f'{days}-{hours:02d}:{minutes:02d}:{seconds:02d}'
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_PROCESS_ID: self.process_id,
            self.FIELD_PARENT_PROCESS_ID: self.parent_process_id,
            self.FIELD_PROCESS_GROUP_ID: self.process_group_id,
            self.FIELD_USER_NAME: self.user_name,
            self.FIELD_USER_ID: self.user_id,
            self.FIELD_REAL_USER_NAME: self.real_user_name,
            self.FIELD_REAL_USER_ID: self.real_user_id,
            self.FIELD_PROCESS_NAME: self.process_name,
            self.FIELD_COMMAND_LINE: self.command_line,
            self.FIELD_CPU_USAGE_PERCENT: self.cpu_usage_percent,
            self.FIELD_MEMORY_USAGE_PERCENT: self.memory_usage_percent,
            self.FIELD_CPU_PROCESS_TIME: self._fmt_timedelta(self.cpu_process_time),
            self.FIELD_ELAPSED_SINCE_START: self._fmt_timedelta(self.elapsed_since_start),
            self.FIELD_STARTED_AT: self._fmt_datetime(self.started_at),
            self.FIELD_STATUS: self.status,
            self.FIELD_TERMINAL: self.terminal,
            self.FIELD_PRIORITY: self.priority,
            self.FIELD_NICE_VALUE: self.nice_value,
            self.FIELD_SCHEDULER_CLASS: self.scheduler_class,
            self.FIELD_SCHEDULER_POLICY: self.scheduler_policy,
            self.FIELD_REALTIME_PRIORITY: self.realtime_priority,
            self.FIELD_VIRTUAL_MEMORY_KB: self.virtual_memory_kb,
            self.FIELD_RESIDENT_MEMORY_KB: self.resident_memory_kb,
            self.FIELD_CURRENT_CPU: self.current_cpu,
            self.FIELD_CGROUP_PATH: self.cgroup_path,
            self.FIELD_THREADS: self.threads,
            self.FIELD_WAIT_CHANNEL: self.wait_channel,
            self.FIELD_KERNEL_FLAGS: self.kernel_flags,
            self.FIELD_MAJOR_PAGE_FAULTS: self.major_page_faults,
            self.FIELD_MINOR_PAGE_FAULTS: self.minor_page_faults,
            self.FIELD_SESSION_ID: self.session_id,
            self.FIELD_THREAD_GROUP_ID: self.thread_group_id,
        }
    
    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, rows: List[Dict[str, Any]]) -> List['ProcessInfo']:
        return [cls.from_dict(r) for r in (rows or [])]

    @staticmethod
    def list_to_dicts(items: List['ProcessInfo']) -> List[Dict[str, Any]]:
        return [i.to_public() for i in (items or [])]

    @classmethod
    def list_to_public(cls, items: List['ProcessInfo']) -> List[Dict[str, Any]]:
        return cls.list_to_dicts(items)

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_PROCESS_ID: {'type': ['integer', 'null'], 'example': 1234},
                cls.FIELD_PARENT_PROCESS_ID: {'type': ['integer', 'null'], 'example': 1},
                cls.FIELD_PROCESS_GROUP_ID: {'type': ['integer', 'null'], 'example': 1234},
                cls.FIELD_USER_NAME: {'type': ['string', 'null'], 'example': 'root'},
                cls.FIELD_USER_ID: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_REAL_USER_NAME: {'type': ['string', 'null'], 'example': 'alice'},
                cls.FIELD_REAL_USER_ID: {'type': ['integer', 'null'], 'example': 1000},
                cls.FIELD_PROCESS_NAME: {'type': ['string', 'null'], 'example': 'bash'},
                cls.FIELD_COMMAND_LINE: {'type': ['string', 'null'], 'example': '/bin/bash --login'},
                cls.FIELD_CPU_USAGE_PERCENT: {'type': ['number', 'null'], 'example': 0.1},
                cls.FIELD_MEMORY_USAGE_PERCENT: {'type': ['number', 'null'], 'example': 0.3},
                cls.FIELD_CPU_PROCESS_TIME: {'type': ['string', 'null'], 'example': '00:00:13'},
                cls.FIELD_ELAPSED_SINCE_START: {'type': ['string', 'null'], 'example': '4-00:25:04'},
                cls.FIELD_STARTED_AT: {'type': ['string', 'null'], 'example': '2025.11.05-21:06:12'},
                cls.FIELD_STATUS: {'type': ['string', 'null'], 'example': 'Ss'},
                cls.FIELD_TERMINAL: {'type': ['string', 'null'], 'example': 'pts/0'},
                cls.FIELD_PRIORITY: {'type': ['integer', 'null'], 'example': 19},
                cls.FIELD_NICE_VALUE: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_SCHEDULER_CLASS: {'type': ['string', 'null'], 'example': 'TS'},
                cls.FIELD_SCHEDULER_POLICY: {'type': ['string', 'null'], 'example': 'TS'},
                cls.FIELD_REALTIME_PRIORITY: {'type': ['string', 'null'], 'example': '-'},
                cls.FIELD_VIRTUAL_MEMORY_KB: {'type': ['integer', 'null'], 'example': 25464},
                cls.FIELD_RESIDENT_MEMORY_KB: {'type': ['integer', 'null'], 'example': 14448},
                cls.FIELD_CURRENT_CPU: {'type': ['integer', 'null'], 'example': 3},
                cls.FIELD_CGROUP_PATH: {'type': ['string', 'null'], 'example': '0::/init.scope'},
                cls.FIELD_THREADS: {'type': ['integer', 'null'], 'example': 1},
                cls.FIELD_WAIT_CHANNEL: {'type': ['string', 'null'], 'example': '-'},
                cls.FIELD_KERNEL_FLAGS: {'type': ['string', 'null'], 'example': '0'},
                cls.FIELD_MAJOR_PAGE_FAULTS: {'type': ['integer', 'null'], 'example': 104},
                cls.FIELD_MINOR_PAGE_FAULTS: {'type': ['integer', 'null'], 'example': 65379},
                cls.FIELD_SESSION_ID: {'type': ['integer', 'null'], 'example': 1},
                cls.FIELD_THREAD_GROUP_ID: {'type': ['integer', 'null'], 'example': 1},
            },
            'required': [],
            'additionalProperties': False,
        }
    
    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }