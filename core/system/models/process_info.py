from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from core.system.models._conversion import datetime_from_str, datetime_to_str, timedelta_from_seconds, timedelta_to_seconds


@dataclass
class ProcessInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

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

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    process_id: Optional[int] = None
    parent_process_id: Optional[int] = None
    process_group_id: Optional[int] = None
    user_name: Optional[str] = None
    user_id: Optional[int] = None
    real_user_name: Optional[str] = None
    real_user_id: Optional[int] = None
    process_name: Optional[str] = None
    command_line: Optional[str] = None
    cpu_usage_percent: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    cpu_process_time: Optional[timedelta] = None
    elapsed_since_start: Optional[timedelta] = None
    started_at: Optional[datetime] = None
    status: Optional[str] = None
    terminal: Optional[str] = None
    priority: Optional[int] = None
    nice_value: Optional[int] = None
    scheduler_class: Optional[str] = None
    scheduler_policy: Optional[str] = None
    realtime_priority: Optional[str] = None
    virtual_memory_kb: Optional[int] = None
    resident_memory_kb: Optional[int] = None
    current_cpu: Optional[int] = None
    cgroup_path: Optional[str] = None
    threads: Optional[int] = None
    wait_channel: Optional[str] = None
    kernel_flags: Optional[str] = None
    major_page_faults: Optional[int] = None
    minor_page_faults: Optional[int] = None
    session_id: Optional[int] = None
    thread_group_id: Optional[int] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ProcessInfo:
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
            cpu_process_time=timedelta_from_seconds(d.get(cls.FIELD_CPU_PROCESS_TIME)),
            elapsed_since_start=timedelta_from_seconds(d.get(cls.FIELD_ELAPSED_SINCE_START)),
            started_at=datetime_from_str(d.get(cls.FIELD_STARTED_AT)),
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
            self.FIELD_CPU_PROCESS_TIME: timedelta_to_seconds(self.cpu_process_time),
            self.FIELD_ELAPSED_SINCE_START: timedelta_to_seconds(self.elapsed_since_start),
            self.FIELD_STARTED_AT: datetime_to_str(self.started_at),
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
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_PROCESS_ID: {'type': 'integer', 'nullable': True, 'example': 1234, 'description': 'Process ID.'},
                cls.FIELD_PARENT_PROCESS_ID: {'type': 'integer', 'nullable': True, 'example': 1, 'description': 'Parent process ID.'},
                cls.FIELD_PROCESS_GROUP_ID: {'type': 'integer', 'nullable': True, 'example': 1234, 'description': 'Process group ID.'},
                cls.FIELD_USER_NAME: {'type': 'string', 'nullable': True, 'example': 'pi', 'description': 'Effective user name.'},
                cls.FIELD_USER_ID: {'type': 'integer', 'nullable': True, 'example': 1000, 'description': 'Effective user ID.'},
                cls.FIELD_REAL_USER_NAME: {'type': 'string', 'nullable': True, 'example': 'pi', 'description': 'Real user name that started the process.'},
                cls.FIELD_REAL_USER_ID: {'type': 'integer', 'nullable': True, 'example': 1000, 'description': 'Real user ID.'},
                cls.FIELD_PROCESS_NAME: {'type': 'string', 'nullable': True, 'example': 'python', 'description': 'Process executable name.'},
                cls.FIELD_COMMAND_LINE: {'type': 'string', 'nullable': True, 'example': 'python app.py', 'description': 'Full command line.'},
                cls.FIELD_CPU_USAGE_PERCENT: {'type': 'number', 'nullable': True, 'example': 2.5, 'description': 'CPU usage percentage.'},
                cls.FIELD_MEMORY_USAGE_PERCENT: {'type': 'number', 'nullable': True, 'example': 1.2, 'description': 'RAM usage percentage.'},
                cls.FIELD_CPU_PROCESS_TIME: {'type': 'number', 'nullable': True, 'example': 12.34, 'description': 'Total CPU time consumed by the process in seconds.'},
                cls.FIELD_ELAPSED_SINCE_START: {'type': 'number', 'nullable': True, 'example': 3600.0, 'description': 'Elapsed process lifetime in seconds.'},
                cls.FIELD_STARTED_AT: {'type': 'string', 'nullable': True, 'example': '2026-04-29T12:00:00', 'description': 'Process start date and time.'},
                cls.FIELD_STATUS: {'type': 'string', 'nullable': True, 'example': 'running', 'description': 'Process status.'},
                cls.FIELD_TERMINAL: {'type': 'string', 'nullable': True, 'example': 'pts/0', 'description': 'Terminal attached to the process.'},
                cls.FIELD_PRIORITY: {'type': 'integer', 'nullable': True, 'example': 20, 'description': 'Kernel process priority.'},
                cls.FIELD_NICE_VALUE: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Nice value.'},
                cls.FIELD_SCHEDULER_CLASS: {'type': 'string', 'nullable': True, 'example': 'TS', 'description': 'Scheduler class.'},
                cls.FIELD_SCHEDULER_POLICY: {'type': 'string', 'nullable': True, 'example': 'SCHED_OTHER', 'description': 'Scheduler policy.'},
                cls.FIELD_REALTIME_PRIORITY: {'type': 'string', 'nullable': True, 'example': '-', 'description': 'Real-time priority.'},
                cls.FIELD_VIRTUAL_MEMORY_KB: {'type': 'integer', 'nullable': True, 'example': 102400, 'description': 'Virtual memory size in KB.'},
                cls.FIELD_RESIDENT_MEMORY_KB: {'type': 'integer', 'nullable': True, 'example': 20480, 'description': 'Resident memory size in KB.'},
                cls.FIELD_CURRENT_CPU: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Current CPU core number.'},
                cls.FIELD_CGROUP_PATH: {'type': 'string', 'nullable': True, 'example': '/system.slice/ssh.service', 'description': 'Assigned cgroup path.'},
                cls.FIELD_THREADS: {'type': 'integer', 'nullable': True, 'example': 4, 'description': 'Number of process threads.'},
                cls.FIELD_WAIT_CHANNEL: {'type': 'string', 'nullable': True, 'example': 'do_wait', 'description': 'Kernel wait channel.'},
                cls.FIELD_KERNEL_FLAGS: {'type': 'string', 'nullable': True, 'example': '0x00400000', 'description': 'Kernel process flags.'},
                cls.FIELD_MAJOR_PAGE_FAULTS: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Major page fault count.'},
                cls.FIELD_MINOR_PAGE_FAULTS: {'type': 'integer', 'nullable': True, 'example': 123, 'description': 'Minor page fault count.'},
                cls.FIELD_SESSION_ID: {'type': 'integer', 'nullable': True, 'example': 1234, 'description': 'Session ID.'},
                cls.FIELD_THREAD_GROUP_ID: {'type': 'integer', 'nullable': True, 'example': 1234, 'description': 'Thread group ID.'},
            },
            'required': [],
        }
