from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class BtAddressRequest(PublicDataModel):

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
    def from_dict(cls, d: Dict[str, Any]) -> BtAddressRequest:
        return cls(address=str(d[cls.FIELD_ADDRESS]))

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
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '00:11:22:33:44:55'},
            },
            'required': [cls.FIELD_ADDRESS],
        }
