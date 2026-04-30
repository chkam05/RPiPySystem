from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class BtReceivedCountResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_COUNT: ClassVar[str] = 'count'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    count: int

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtReceivedCountResponse:
        return cls(count=int(d.get(cls.FIELD_COUNT, 0)))

    def to_dict(self) -> Dict[str, Any]:
        return {self.FIELD_COUNT: self.count}

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_COUNT: {'type': 'integer', 'example': 1},
            },
            'required': [cls.FIELD_COUNT],
        }
