from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from core.system.models._conversion import datetime_from_str, datetime_to_str, timedelta_from_seconds, timedelta_to_seconds


@dataclass
class OSUserLoggedIn(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_USER_NAME: ClassVar[str] = 'user_name'
    FIELD_TERMINAL_NAME: ClassVar[str] = 'terminal_name'
    FIELD_LOGGED_AT: ClassVar[str] = 'logged_at'
    FIELD_REMOTE_HOST: ClassVar[str] = 'remote_host'
    FIELD_IDLE_TIME: ClassVar[str] = 'idle_time'
    FIELD_JOB_CPU_TIME: ClassVar[str] = 'job_cpu_time'
    FIELD_PROCESS_CPU_TIME: ClassVar[str] = 'process_cpu_time'
    FIELD_SESSION_COMMAND: ClassVar[str] = 'session_command'
    FIELD_PROCESS_ID: ClassVar[str] = 'process_id'
    FIELD_SESSION_COMMENT: ClassVar[str] = 'session_comment'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    user_name: str
    terminal_name: Optional[str] = None
    logged_at: Optional[datetime] = None
    remote_host: Optional[str] = None
    idle_time: Optional[timedelta] = None
    job_cpu_time: Optional[float] = None
    process_cpu_time: Optional[float] = None
    session_command: Optional[str] = None
    process_id: Optional[int] = None
    session_comment: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> OSUserLoggedIn:
        return cls(
            user_name=d[cls.FIELD_USER_NAME],
            terminal_name=d.get(cls.FIELD_TERMINAL_NAME),
            logged_at=datetime_from_str(d.get(cls.FIELD_LOGGED_AT)),
            remote_host=d.get(cls.FIELD_REMOTE_HOST),
            idle_time=timedelta_from_seconds(d.get(cls.FIELD_IDLE_TIME)),
            job_cpu_time=d.get(cls.FIELD_JOB_CPU_TIME),
            process_cpu_time=d.get(cls.FIELD_PROCESS_CPU_TIME),
            session_command=d.get(cls.FIELD_SESSION_COMMAND),
            process_id=d.get(cls.FIELD_PROCESS_ID),
            session_comment=d.get(cls.FIELD_SESSION_COMMENT),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_USER_NAME: self.user_name,
            self.FIELD_TERMINAL_NAME: self.terminal_name,
            self.FIELD_LOGGED_AT: datetime_to_str(self.logged_at),
            self.FIELD_REMOTE_HOST: self.remote_host,
            self.FIELD_IDLE_TIME: timedelta_to_seconds(self.idle_time),
            self.FIELD_JOB_CPU_TIME: self.job_cpu_time,
            self.FIELD_PROCESS_CPU_TIME: self.process_cpu_time,
            self.FIELD_SESSION_COMMAND: self.session_command,
            self.FIELD_PROCESS_ID: self.process_id,
            self.FIELD_SESSION_COMMENT: self.session_comment,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_USER_NAME: {'type': 'string', 'example': 'pi', 'description': 'Logged-in user name.'},
                cls.FIELD_TERMINAL_NAME: {'type': 'string', 'nullable': True, 'example': 'pts/0', 'description': 'Terminal name.'},
                cls.FIELD_LOGGED_AT: {'type': 'string', 'nullable': True, 'example': '2026-04-29T12:00:00', 'description': 'Login date and time.'},
                cls.FIELD_REMOTE_HOST: {'type': 'string', 'nullable': True, 'example': '192.168.1.10', 'description': 'Remote host for SSH or remote terminal sessions.'},
                cls.FIELD_IDLE_TIME: {'type': 'number', 'nullable': True, 'example': 120.0, 'description': 'Idle time in seconds.'},
                cls.FIELD_JOB_CPU_TIME: {'type': 'number', 'nullable': True, 'example': 1.5, 'description': 'Session job CPU time in seconds.'},
                cls.FIELD_PROCESS_CPU_TIME: {'type': 'number', 'nullable': True, 'example': 0.3, 'description': 'Session process CPU time in seconds.'},
                cls.FIELD_SESSION_COMMAND: {'type': 'string', 'nullable': True, 'example': 'sshd: pi [priv]', 'description': 'Session command or process description.'},
                cls.FIELD_PROCESS_ID: {'type': 'integer', 'nullable': True, 'example': 1234, 'description': 'Session process ID.'},
                cls.FIELD_SESSION_COMMENT: {'type': 'string', 'nullable': True, 'example': '192.168.1.10', 'description': 'Additional session comment.'},
            },
            'required': [cls.FIELD_USER_NAME],
        }
