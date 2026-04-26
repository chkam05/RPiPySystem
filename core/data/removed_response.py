from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class RemovedResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_REMOVED: ClassVar[str] = 'removed'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    removed: bool = True

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RemovedResponse:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            removed=d[cls.FIELD_REMOVED]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_REMOVED: self.removed
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_REMOVED: {'type': 'boolean', 'example': True}
            },
            'required': [cls.FIELD_REMOVED],
        }
