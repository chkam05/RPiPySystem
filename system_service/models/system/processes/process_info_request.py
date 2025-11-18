from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='ProcessInfoRequest')


@dataclass
class ProcessInfoRequest(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

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

    # --- DEFAULT VALUES ---

    DEFAULT_PROCESS_ID: ClassVar[bool] = True
    DEFAULT_PARENT_PROCESS_ID: ClassVar[bool] = False
    DEFAULT_PROCESS_GROUP_ID: ClassVar[bool] = False
    DEFAULT_USER_NAME: ClassVar[bool] = True
    DEFAULT_USER_ID: ClassVar[bool] = False
    DEFAULT_REAL_USER_NAME: ClassVar[bool] = False
    DEFAULT_REAL_USER_ID: ClassVar[bool] = False
    DEFAULT_PROCESS_NAME: ClassVar[bool] = False
    DEFAULT_COMMAND_LINE: ClassVar[bool] = True
    DEFAULT_CPU_USAGE_PERCENT: ClassVar[bool] = True
    DEFAULT_MEMORY_USAGE_PERCENT: ClassVar[bool] = True
    DEFAULT_CPU_PROCESS_TIME: ClassVar[bool] = True
    DEFAULT_ELAPSED_SINCE_START: ClassVar[bool] = False
    DEFAULT_STARTED_AT: ClassVar[bool] = True
    DEFAULT_STATUS: ClassVar[bool] = True
    DEFAULT_TERMINAL: ClassVar[bool] = True
    DEFAULT_PRIORITY: ClassVar[bool] = False
    DEFAULT_NICE_VALUE: ClassVar[bool] = False
    DEFAULT_SCHEDULER_CLASS: ClassVar[bool] = False
    DEFAULT_SCHEDULER_POLICY: ClassVar[bool] = False
    DEFAULT_REALTIME_PRIORITY: ClassVar[bool] = False
    DEFAULT_VIRTUAL_MEMORY_KB: ClassVar[bool] = True
    DEFAULT_RESIDENT_MEMORY_KB: ClassVar[bool] = True
    DEFAULT_CURRENT_CPU: ClassVar[bool] = False
    DEFAULT_CGROUP_PATH: ClassVar[bool] = False
    DEFAULT_THREADS: ClassVar[bool] = False
    DEFAULT_WAIT_CHANNEL: ClassVar[bool] = False
    DEFAULT_KERNEL_FLAGS: ClassVar[bool] = False
    DEFAULT_MAJOR_PAGE_FAULTS: ClassVar[bool] = False
    DEFAULT_MINOR_PAGE_FAULTS: ClassVar[bool] = False
    DEFAULT_SESSION_ID: ClassVar[bool] = False
    DEFAULT_THREAD_GROUP_ID: ClassVar[bool] = False

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    process_id: bool
    parent_process_id: bool
    process_group_id: bool
    user_name: bool             # effective user
    user_id: bool               # effective uid
    real_user_name: bool        # ruser
    real_user_id: bool          # ruid
    process_name: bool          # comm
    command_line: bool          # args/cmd
    cpu_usage_percent: bool     # %CPU
    memory_usage_percent: bool  # %MEM
    cpu_process_time: bool      # timedelta
    elapsed_since_start: bool   # timedelta
    started_at: bool            # datetime
    status: bool                # stat (full)
    terminal: bool              # tty
    priority: bool              # pri
    nice_value: bool            # nice
    scheduler_class: bool       # cls
    scheduler_policy: bool      # policy
    realtime_priority: bool     # rtprio
    virtual_memory_kb: bool     # vsz
    resident_memory_kb: bool    # rss
    current_cpu: bool           # psr
    cgroup_path: bool           # cgroup
    threads: bool               # nlwp
    wait_channel: bool          # wchan
    kernel_flags: bool          # flags/f
    major_page_faults: bool     # maj_flt
    minor_page_faults: bool     # min_flt
    session_id: bool            # sid
    thread_group_id: bool       # tgid

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def default(cls) -> ProcessInfoRequest:
        return cls(
            process_id=cls.DEFAULT_PROCESS_ID,
            parent_process_id=cls.DEFAULT_PARENT_PROCESS_ID,
            process_group_id=cls.DEFAULT_PROCESS_GROUP_ID,
            user_name=cls.DEFAULT_USER_NAME,
            user_id=cls.DEFAULT_USER_ID,
            real_user_name=cls.DEFAULT_REAL_USER_NAME,
            real_user_id=cls.DEFAULT_REAL_USER_ID,
            process_name=cls.DEFAULT_PROCESS_NAME,
            command_line=cls.DEFAULT_COMMAND_LINE,
            cpu_usage_percent=cls.DEFAULT_CPU_USAGE_PERCENT,
            memory_usage_percent=cls.DEFAULT_MEMORY_USAGE_PERCENT,
            cpu_process_time=cls.DEFAULT_CPU_PROCESS_TIME,
            elapsed_since_start=cls.DEFAULT_ELAPSED_SINCE_START,
            started_at=cls.DEFAULT_STARTED_AT,
            status=cls.DEFAULT_STATUS,
            terminal=cls.DEFAULT_TERMINAL,
            priority=cls.DEFAULT_PRIORITY,
            nice_value=cls.DEFAULT_NICE_VALUE,
            scheduler_class=cls.DEFAULT_SCHEDULER_CLASS,
            scheduler_policy=cls.DEFAULT_SCHEDULER_POLICY,
            realtime_priority=cls.DEFAULT_REALTIME_PRIORITY,
            virtual_memory_kb=cls.DEFAULT_VIRTUAL_MEMORY_KB,
            resident_memory_kb=cls.DEFAULT_RESIDENT_MEMORY_KB,
            current_cpu=cls.DEFAULT_CURRENT_CPU,
            cgroup_path=cls.DEFAULT_CGROUP_PATH,
            threads=cls.DEFAULT_THREADS,
            wait_channel=cls.DEFAULT_WAIT_CHANNEL,
            kernel_flags=cls.DEFAULT_KERNEL_FLAGS,
            major_page_faults=cls.DEFAULT_MAJOR_PAGE_FAULTS,
            minor_page_faults=cls.DEFAULT_MINOR_PAGE_FAULTS,
            session_id=cls.DEFAULT_SESSION_ID,
            thread_group_id=cls.DEFAULT_THREAD_GROUP_ID,
        )

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> ProcessInfoRequest:
        return cls(
            process_id=d.get(cls.FIELD_PROCESS_ID, cls.DEFAULT_PROCESS_ID),
            parent_process_id=d.get(cls.FIELD_PARENT_PROCESS_ID, cls.DEFAULT_PARENT_PROCESS_ID),
            process_group_id=d.get(cls.FIELD_PROCESS_GROUP_ID, cls.DEFAULT_PROCESS_GROUP_ID),
            user_name=d.get(cls.FIELD_USER_NAME, cls.DEFAULT_USER_NAME),
            user_id=d.get(cls.FIELD_USER_ID, cls.DEFAULT_USER_ID),
            real_user_name=d.get(cls.FIELD_REAL_USER_NAME, cls.DEFAULT_REAL_USER_NAME),
            real_user_id=d.get(cls.FIELD_REAL_USER_ID, cls.DEFAULT_REAL_USER_ID),
            process_name=d.get(cls.FIELD_PROCESS_NAME, cls.DEFAULT_PROCESS_NAME),
            command_line=d.get(cls.FIELD_COMMAND_LINE, cls.DEFAULT_COMMAND_LINE),
            cpu_usage_percent=d.get(cls.FIELD_CPU_USAGE_PERCENT, cls.DEFAULT_CPU_USAGE_PERCENT),
            memory_usage_percent=d.get(cls.FIELD_MEMORY_USAGE_PERCENT, cls.DEFAULT_MEMORY_USAGE_PERCENT),
            cpu_process_time=d.get(cls.FIELD_CPU_PROCESS_TIME, cls.DEFAULT_CPU_PROCESS_TIME),
            elapsed_since_start=d.get(cls.FIELD_ELAPSED_SINCE_START, cls.DEFAULT_ELAPSED_SINCE_START),
            started_at=d.get(cls.FIELD_STARTED_AT, cls.DEFAULT_STARTED_AT),
            status=d.get(cls.FIELD_STATUS, cls.DEFAULT_STATUS),
            terminal=d.get(cls.FIELD_TERMINAL, cls.DEFAULT_TERMINAL),
            priority=d.get(cls.FIELD_PRIORITY, cls.DEFAULT_PRIORITY),
            nice_value=d.get(cls.FIELD_NICE_VALUE, cls.DEFAULT_NICE_VALUE),
            scheduler_class=d.get(cls.FIELD_SCHEDULER_CLASS, cls.DEFAULT_SCHEDULER_CLASS),
            scheduler_policy=d.get(cls.FIELD_SCHEDULER_POLICY, cls.DEFAULT_SCHEDULER_POLICY),
            realtime_priority=d.get(cls.FIELD_REALTIME_PRIORITY, cls.DEFAULT_REALTIME_PRIORITY),
            virtual_memory_kb=d.get(cls.FIELD_VIRTUAL_MEMORY_KB, cls.DEFAULT_VIRTUAL_MEMORY_KB),
            resident_memory_kb=d.get(cls.FIELD_RESIDENT_MEMORY_KB, cls.DEFAULT_RESIDENT_MEMORY_KB),
            current_cpu=d.get(cls.FIELD_CURRENT_CPU, cls.DEFAULT_CURRENT_CPU),
            cgroup_path=d.get(cls.FIELD_CGROUP_PATH, cls.DEFAULT_CGROUP_PATH),
            threads=d.get(cls.FIELD_THREADS, cls.DEFAULT_THREADS),
            wait_channel=d.get(cls.FIELD_WAIT_CHANNEL, cls.DEFAULT_WAIT_CHANNEL),
            kernel_flags=d.get(cls.FIELD_KERNEL_FLAGS, cls.DEFAULT_KERNEL_FLAGS),
            major_page_faults=d.get(cls.FIELD_MAJOR_PAGE_FAULTS, cls.DEFAULT_MAJOR_PAGE_FAULTS),
            minor_page_faults=d.get(cls.FIELD_MINOR_PAGE_FAULTS, cls.DEFAULT_MINOR_PAGE_FAULTS),
            session_id=d.get(cls.FIELD_SESSION_ID, cls.DEFAULT_SESSION_ID),
            thread_group_id=d.get(cls.FIELD_THREAD_GROUP_ID, cls.DEFAULT_THREAD_GROUP_ID),
        )

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
            self.FIELD_CPU_PROCESS_TIME: self.cpu_process_time,
            self.FIELD_ELAPSED_SINCE_START: self.elapsed_since_start,
            self.FIELD_STARTED_AT: self.started_at,
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
            self.FIELD_THREAD_GROUP_ID: self.thread_group_id
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_PROCESS_ID: {'type': 'boolean', 'default': cls.DEFAULT_PROCESS_ID},
                cls.FIELD_PARENT_PROCESS_ID: {'type': 'boolean', 'default': cls.DEFAULT_PARENT_PROCESS_ID},
                cls.FIELD_PROCESS_GROUP_ID: {'type': 'boolean', 'default': cls.DEFAULT_PROCESS_GROUP_ID},
                cls.FIELD_USER_NAME: {'type': 'boolean', 'default': cls.DEFAULT_USER_NAME},
                cls.FIELD_USER_ID: {'type': 'boolean', 'default': cls.DEFAULT_USER_ID},
                cls.FIELD_REAL_USER_NAME: {'type': 'boolean', 'default': cls.DEFAULT_REAL_USER_NAME},
                cls.FIELD_REAL_USER_ID: {'type': 'boolean', 'default': cls.DEFAULT_REAL_USER_ID},
                cls.FIELD_PROCESS_NAME: {'type': 'boolean', 'default': cls.DEFAULT_PROCESS_NAME},
                cls.FIELD_COMMAND_LINE: {'type': 'boolean', 'default': cls.DEFAULT_COMMAND_LINE},
                cls.FIELD_CPU_USAGE_PERCENT: {'type': 'boolean', 'default': cls.DEFAULT_CPU_USAGE_PERCENT},
                cls.FIELD_MEMORY_USAGE_PERCENT: {'type': 'boolean', 'default': cls.DEFAULT_MEMORY_USAGE_PERCENT},
                cls.FIELD_CPU_PROCESS_TIME: {'type': 'boolean', 'default': cls.DEFAULT_CPU_PROCESS_TIME},
                cls.FIELD_ELAPSED_SINCE_START: {'type': 'boolean', 'default': cls.DEFAULT_ELAPSED_SINCE_START},
                cls.FIELD_STARTED_AT: {'type': 'boolean', 'default': cls.DEFAULT_STARTED_AT},
                cls.FIELD_STATUS: {'type': 'boolean', 'default': cls.DEFAULT_STATUS},
                cls.FIELD_TERMINAL: {'type': 'boolean', 'default': cls.DEFAULT_TERMINAL},
                cls.FIELD_PRIORITY: {'type': 'boolean', 'default': cls.DEFAULT_PRIORITY},
                cls.FIELD_NICE_VALUE: {'type': 'boolean', 'default': cls.DEFAULT_NICE_VALUE},
                cls.FIELD_SCHEDULER_CLASS: {'type': 'boolean', 'default': cls.DEFAULT_SCHEDULER_CLASS},
                cls.FIELD_SCHEDULER_POLICY: {'type': 'boolean', 'default': cls.DEFAULT_SCHEDULER_POLICY},
                cls.FIELD_REALTIME_PRIORITY: {'type': 'boolean', 'default': cls.DEFAULT_REALTIME_PRIORITY},
                cls.FIELD_VIRTUAL_MEMORY_KB: {'type': 'boolean', 'default': cls.DEFAULT_VIRTUAL_MEMORY_KB},
                cls.FIELD_RESIDENT_MEMORY_KB: {'type': 'boolean', 'default': cls.DEFAULT_RESIDENT_MEMORY_KB},
                cls.FIELD_CURRENT_CPU: {'type': 'boolean', 'default': cls.DEFAULT_CURRENT_CPU},
                cls.FIELD_CGROUP_PATH: {'type': 'boolean', 'default': cls.DEFAULT_CGROUP_PATH},
                cls.FIELD_THREADS: {'type': 'boolean', 'default': cls.DEFAULT_THREADS},
                cls.FIELD_WAIT_CHANNEL: {'type': 'boolean', 'default': cls.DEFAULT_WAIT_CHANNEL},
                cls.FIELD_KERNEL_FLAGS: {'type': 'boolean', 'default': cls.DEFAULT_KERNEL_FLAGS},
                cls.FIELD_MAJOR_PAGE_FAULTS: {'type': 'boolean', 'default': cls.DEFAULT_MAJOR_PAGE_FAULTS},
                cls.FIELD_MINOR_PAGE_FAULTS: {'type': 'boolean', 'default': cls.DEFAULT_MINOR_PAGE_FAULTS},
                cls.FIELD_SESSION_ID: {'type': 'boolean', 'default': cls.DEFAULT_SESSION_ID},
                cls.FIELD_THREAD_GROUP_ID: {'type': 'boolean', 'default': cls.DEFAULT_THREAD_GROUP_ID},
            },
            'required': [],
        }