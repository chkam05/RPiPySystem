from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class IOCommand(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_ACTION: ClassVar[str] = 'action'
    FIELD_TARGET: ClassVar[str] = 'target'
    FIELD_PAYLOAD: ClassVar[str] = 'payload'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    action: str
    target: str = 'service'
    payload: Dict[str, Any] = field(default_factory=dict)

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> IOCommand:
        return cls(
            action=str(d[cls.FIELD_ACTION]),
            target=str(d.get(cls.FIELD_TARGET, 'service')),
            payload=dict(d.get(cls.FIELD_PAYLOAD, {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_ACTION: self.action,
            self.FIELD_TARGET: self.target,
            self.FIELD_PAYLOAD: self.payload,
        }
