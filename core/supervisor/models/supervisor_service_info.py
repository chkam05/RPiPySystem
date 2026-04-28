from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class SupervisorServiceInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

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

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    full_name: str
    name: str
    group: str
    state: Optional[str] = None
    state_code: Optional[int] = None
    pid: Optional[int] = None
    description: Optional[str] = None
    start: Optional[datetime] = None
    stop: Optional[datetime] = None
    now: Optional[datetime] = None
    exitstatus: Optional[int] = None
    spawnerr: Optional[str] = None
    stdout_logfile: Optional[str] = None
    stderr_logfile: Optional[str] = None

    # --------------------------------------------------------------------------------
    # CONVERSION
    # --------------------------------------------------------------------------------

    @staticmethod
    def _datetime_from_value(value: Any) -> Optional[datetime]:
        if value is None or value == '':
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except ValueError:
                pass
        try:
            epoch = int(value)
        except (TypeError, ValueError):
            return None
        if epoch <= 0:
            return None
        return datetime.fromtimestamp(epoch, timezone.utc)

    @staticmethod
    def _datetime_to_str(value: Any) -> Optional[str]:
        dt = SupervisorServiceInfo._datetime_from_value(value)
        if dt is None:
            return None
        return dt.isoformat(timespec='seconds')

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> SupervisorServiceInfo:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            full_name=d.get(cls.FIELD_FULL_NAME),
            name=d.get(cls.FIELD_NAME),
            group=d.get(cls.FIELD_GROUP),
            state=d.get(cls.FIELD_STATE),
            state_code=d.get(cls.FIELD_STATE_CODE),
            pid=d.get(cls.FIELD_PID),
            description=d.get(cls.FIELD_DESCRIPTION),
            start=cls._datetime_from_value(d.get(cls.FIELD_START)),
            stop=cls._datetime_from_value(d.get(cls.FIELD_STOP)),
            now=cls._datetime_from_value(d.get(cls.FIELD_NOW)),
            exitstatus=d.get(cls.FIELD_EXITSTATUS),
            spawnerr=d.get(cls.FIELD_SPAWNERR),
            stdout_logfile=d.get(cls.FIELD_STDOUT_LOGFILE),
            stderr_logfile=d.get(cls.FIELD_STDERR_LOGFILE)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_FULL_NAME: self.full_name,
            self.FIELD_NAME: self.name,
            self.FIELD_GROUP: self.group,
            self.FIELD_STATE: self.state,
            self.FIELD_STATE_CODE: self.state_code,
            self.FIELD_PID: self.pid,
            self.FIELD_DESCRIPTION: self.description,
            self.FIELD_START: self._datetime_to_str(self.start),
            self.FIELD_STOP: self._datetime_to_str(self.stop),
            self.FIELD_NOW: self._datetime_to_str(self.now),
            self.FIELD_EXITSTATUS: self.exitstatus,
            self.FIELD_SPAWNERR: self.spawnerr,
            self.FIELD_STDOUT_LOGFILE: self.stdout_logfile,
            self.FIELD_STDERR_LOGFILE: self.stderr_logfile,
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

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
                cls.FIELD_START: {'type': 'string', 'nullable': True, 'example': '2026-04-28T23:36:10+00:00'},
                cls.FIELD_STOP: {'type': 'string', 'nullable': True, 'example': '2026-04-28T23:36:10+00:00'},
                cls.FIELD_NOW: {'type': 'string', 'nullable': True, 'example': '2026-04-28T23:36:10+00:00'},
                cls.FIELD_EXITSTATUS: {'type': 'integer', 'example': 0},
                cls.FIELD_SPAWNERR: {'type': 'string', 'example': ''},
                cls.FIELD_STDOUT_LOGFILE: {'type': 'string', 'example': '/var/log/worker.out'},
                cls.FIELD_STDERR_LOGFILE: {'type': 'string', 'example': '/var/log/worker.err'},
            },
            'required': [],
        }
    
    @classmethod
    def schema_public_short(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_FULL_NAME: {'type': 'string', 'example': 'group:worker'},
                cls.FIELD_NAME: {'type': 'string', 'example': 'worker'},
                cls.FIELD_GROUP: {'type': 'string', 'example': 'group'}
            },
            'required': [],
        }
