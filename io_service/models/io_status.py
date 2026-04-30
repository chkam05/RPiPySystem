from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class IOStatus(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_SERVICE: ClassVar[str] = 'service'
    FIELD_RUNNING: ClassVar[str] = 'running'
    FIELD_LOOP_COUNT: ClassVar[str] = 'loop_count'
    FIELD_UPDATED_AT: ClassVar[str] = 'updated_at'
    FIELD_COMPONENTS: ClassVar[str] = 'components'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    service: str
    running: bool = False
    loop_count: int = 0
    updated_at: datetime = field(default_factory=datetime.now)
    components: Dict[str, Any] = field(default_factory=dict)

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> IOStatus:
        return cls(
            service=d[cls.FIELD_SERVICE],
            running=bool(d.get(cls.FIELD_RUNNING, False)),
            loop_count=int(d.get(cls.FIELD_LOOP_COUNT, 0)),
            updated_at=datetime.fromisoformat(d[cls.FIELD_UPDATED_AT]) if d.get(cls.FIELD_UPDATED_AT) else datetime.now(),
            components=dict(d.get(cls.FIELD_COMPONENTS, {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_SERVICE: self.service,
            self.FIELD_RUNNING: self.running,
            self.FIELD_LOOP_COUNT: self.loop_count,
            self.FIELD_UPDATED_AT: self.updated_at.isoformat(timespec='seconds'),
            self.FIELD_COMPONENTS: self.components,
        }
