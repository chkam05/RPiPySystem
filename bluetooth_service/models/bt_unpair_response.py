from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class BtUnpairResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_REMOVED: ClassVar[str] = 'removed'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    removed: bool

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtUnpairResponse:
        return cls(removed=bool(d.get(cls.FIELD_REMOVED, False)))

    def to_dict(self) -> Dict[str, Any]:
        return {self.FIELD_REMOVED: self.removed}

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_REMOVED: {'type': 'boolean', 'example': True},
            },
            'required': [cls.FIELD_REMOVED],
        }
