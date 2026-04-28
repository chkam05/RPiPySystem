from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class RefreshRequest(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_REFRESH_TOKEN: ClassVar[str] = 'refresh_token'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    refresh_token: str

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RefreshRequest:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            refresh_token=d[cls.FIELD_REFRESH_TOKEN]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_REFRESH_TOKEN: self.refresh_token
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_REFRESH_TOKEN: {'type': 'string'},
            },
            'required': [cls.FIELD_REFRESH_TOKEN],
        }
