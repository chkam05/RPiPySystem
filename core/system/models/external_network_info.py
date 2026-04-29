from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class ExternalNetworkInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_ADDRESS: ClassVar[str] = 'address'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    address: str

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ExternalNetworkInfo:
        return cls(address=d[cls.FIELD_ADDRESS])

    def to_dict(self) -> Dict[str, Any]:
        return {self.FIELD_ADDRESS: self.address}

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '203.0.113.10', 'description': 'External public IP address.'},
            },
            'required': [cls.FIELD_ADDRESS],
        }
