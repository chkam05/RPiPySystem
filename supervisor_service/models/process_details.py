from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional


@dataclass
class ProcessDetails:
    # --- Field-name constants ---
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_GROUP: ClassVar[str] = 'group'
    FIELD_STATE: ClassVar[str] = 'state'               # string, np. RUNNING
    FIELD_STATE_CODE: ClassVar[str] = 'state_code'     # int (kod Supervisora)
    FIELD_PID: ClassVar[str] = 'pid'                   # int | None
    FIELD_DESCRIPTION: ClassVar[str] = 'description'
    FIELD_START: ClassVar[str] = 'start'               # epoch (int)
    FIELD_STOP: ClassVar[str] = 'stop'                 # epoch (int)
    FIELD_NOW: ClassVar[str] = 'now'                   # epoch (int)
    FIELD_EXITSTATUS: ClassVar[str] = 'exitstatus'     # int
    FIELD_SPAWNERR: ClassVar[str] = 'spawnerr'
    FIELD_STDOUT_LOGFILE: ClassVar[str] = 'stdout_logfile'
    FIELD_STDERR_LOGFILE: ClassVar[str] = 'stderr_logfile'

    # --- Fields ---
    name: str
    group: str
    state: str
    state_code: int
    pid: Optional[int]
    description: str
    start: int
    stop: int
    now: int
    exitstatus: int
    spawnerr: str
    stdout_logfile: str
    stderr_logfile: str

    # --- Utilities ---

    @staticmethod
    def _to_int(raw: Any, default: int = 0) -> int:
        try:
            return int(raw)
        except Exception:
            return default

    @staticmethod
    def _to_optional_int(raw: Any) -> Optional[int]:
        if raw is None or raw == '':
            return None
        try:
            v = int(raw)
            return v if v != 0 else None
        except Exception:
            return None
    
    # --- Packaging methods ---

    @classmethod
    def from_supervisor_dict(cls, d: Dict[str, Any]) -> 'ProcessDetails':
        return cls(
            name=d.get('name', ''),
            group=d.get('group', ''),
            state=str(d.get('statename', '')),
            state_code=cls._to_int(d.get('state', 0)),
            pid=cls._to_optional_int(d.get('pid', None)),
            description=str(d.get('description', '') or ''),
            start=cls._to_int(d.get('start', 0)),
            stop=cls._to_int(d.get('stop', 0)),
            now=cls._to_int(d.get('now', 0)),
            exitstatus=cls._to_int(d.get('exitstatus', 0)),
            spawnerr=str(d.get('spawnerr', '') or ''),
            stdout_logfile=str(d.get('stdout_logfile', '') or ''),
            stderr_logfile=str(d.get('stderr_logfile', '') or ''),
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ProcessDetails':
        return cls(
            name=d[cls.FIELD_NAME],
            group=d.get(cls.FIELD_GROUP, ''),
            state=str(d[cls.FIELD_STATE]),
            state_code=int(d[cls.FIELD_STATE_CODE]),
            pid=cls._to_optional_int(d.get(cls.FIELD_PID)),
            description=str(d.get(cls.FIELD_DESCRIPTION, '') or ''),
            start=int(d.get(cls.FIELD_START, 0)),
            stop=int(d.get(cls.FIELD_STOP, 0)),
            now=int(d.get(cls.FIELD_NOW, 0)),
            exitstatus=int(d.get(cls.FIELD_EXITSTATUS, 0)),
            spawnerr=str(d.get(cls.FIELD_SPAWNERR, '') or ''),
            stdout_logfile=str(d.get(cls.FIELD_STDOUT_LOGFILE, '') or ''),
            stderr_logfile=str(d.get(cls.FIELD_STDERR_LOGFILE, '') or ''),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
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

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'example': 'worker'},
                cls.FIELD_GROUP: {'type': 'string', 'example': 'worker'},
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
            'required': [
                cls.FIELD_NAME, cls.FIELD_GROUP, cls.FIELD_STATE, cls.FIELD_STATE_CODE,
                cls.FIELD_DESCRIPTION, cls.FIELD_START, cls.FIELD_STOP, cls.FIELD_NOW,
                cls.FIELD_EXITSTATUS, cls.FIELD_SPAWNERR, cls.FIELD_STDOUT_LOGFILE, cls.FIELD_STDERR_LOGFILE
            ],
        }