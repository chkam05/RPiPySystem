from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='ServiceDetails')


@dataclass
class ServiceDetails(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_FULL_NAME: ClassVar[str] = 'full_name'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_GROUP: ClassVar[str] = 'group'
    FIELD_STATE: ClassVar[str] = 'state'
    FIELD_STATE_CODE: ClassVar[str] = 'state_code'
    FIELD_PID: ClassVar[str] = 'pid'
    FIELD_DESCRIPTION: ClassVar[str] = 'description'
    FIELD_START: ClassVar[str] = 'start'
    FIELD_STOP: ClassVar[str] = 'stop'
    FIELD_NOW: ClassVar[str] = 'now'
    FIELD_EXITSTATUS: ClassVar[str] = 'exitstatus'
    FIELD_SPAWNERR: ClassVar[str] = 'spawnerr'
    FIELD_STDOUT_LOGFILE: ClassVar[str] = 'stdout_logfile'
    FIELD_STDERR_LOGFILE: ClassVar[str] = 'stderr_logfile'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    full_name: str
    name: str
    group: str
    state: Optional[str]
    state_code: Optional[int]
    pid: Optional[int]
    description: Optional[str]
    start: Optional[int]
    stop: Optional[int]
    now: Optional[int]
    exitstatus: Optional[int]
    spawnerr: Optional[str]
    stdout_logfile: Optional[str]
    stderr_logfile: Optional[str]

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> ServiceDetails:
        return cls(
            full_name=d.get(cls.FIELD_FULL_NAME),
            name=d.get(cls.FIELD_NAME),
            group=d.get(cls.FIELD_GROUP),
            state=d.get(cls.FIELD_STATE),
            state_code=d.get(cls.FIELD_STATE_CODE),
            pid=d.get(cls.FIELD_PID),
            description=d.get(cls.FIELD_DESCRIPTION),
            start=d.get(cls.FIELD_START),
            stop=d.get(cls.FIELD_STOP),
            now=d.get(cls.FIELD_NOW),
            exitstatus=d.get(cls.FIELD_EXITSTATUS),
            spawnerr=d.get(cls.FIELD_SPAWNERR),
            stdout_logfile=d.get(cls.FIELD_STDOUT_LOGFILE),
            stderr_logfile=d.get(cls.FIELD_STDERR_LOGFILE)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_FULL_NAME: self.full_name,
            self.FIELD_NAME: self.name,
            self.FIELD_GROUP: self.group,
            self.FIELD_STATE: self.state,
            self.FIELD_STATE_CODE: self.state_code,
            self.FIELD_PID: self.pid,
            self.FIELD_DESCRIPTION: self.description,
            self.FIELD_START: self.start,
            self.FIELD_STOP: self.stop,
            self.FIELD_NOW: self.now,
            self.FIELD_EXITSTATUS: self.exitstatus,
            self.FIELD_SPAWNERR: self.spawnerr,
            self.FIELD_STDOUT_LOGFILE: self.stdout_logfile,
            self.FIELD_STDERR_LOGFILE: self.stderr_logfile,
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_FULL_NAME: {'type': 'string', 'example': 'group:worker'},
                cls.FIELD_NAME: {'type': 'string', 'example': 'worker'},
                cls.FIELD_GROUP: {'type': 'string', 'example': 'group'},
                cls.FIELD_STATE: {'type': 'string', 'example': 'RUNNING'},
                cls.FIELD_STATE_CODE: {'type': 'integer', 'example': 20},
                cls.FIELD_PID: {'type': 'integer', 'nullable': True, 'example': 1234},
                cls.FIELD_DESCRIPTION: {'type': 'string', 'example': 'pid 1234, uptime 0:02:33'},
                cls.FIELD_START: {'type': 'integer', 'example': 1678252335, 'description': 'epoch seconds'},
                cls.FIELD_STOP: {'type': 'integer', 'example': 0, 'description': 'epoch seconds'},
                cls.FIELD_NOW: {'type': 'integer', 'example': 1678252450, 'description': 'epoch seconds'},
                cls.FIELD_EXITSTATUS: {'type': 'integer', 'example': 0},
                cls.FIELD_SPAWNERR: {'type': 'string', 'example': ''},
                cls.FIELD_STDOUT_LOGFILE: {'type': 'string', 'example': '/var/log/worker.out'},
                cls.FIELD_STDERR_LOGFILE: {'type': 'string', 'example': '/var/log/worker.err'},
            },
            'required': [],
            'additionalProperties': False,
        }