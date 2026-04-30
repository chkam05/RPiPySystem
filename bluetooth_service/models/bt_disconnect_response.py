from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class BtDisconnectResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_DISCONNECTED: ClassVar[str] = 'disconnected'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    disconnected: bool

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtDisconnectResponse:
        return cls(disconnected=bool(d.get(cls.FIELD_DISCONNECTED, False)))

    def to_dict(self) -> Dict[str, Any]:
        return {self.FIELD_DISCONNECTED: self.disconnected}

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_DISCONNECTED: {'type': 'boolean', 'example': True},
            },
            'required': [cls.FIELD_DISCONNECTED],
        }
