from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class BtPairRequest(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_ADDRESS: ClassVar[str] = 'address'
    FIELD_PASSKEY: ClassVar[str] = 'passkey'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    address: str
    passkey: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtPairRequest:
        return cls(address=str(d[cls.FIELD_ADDRESS]), passkey=d.get(cls.FIELD_PASSKEY))

    def to_dict(self) -> Dict[str, Any]:
        return {self.FIELD_ADDRESS: self.address, self.FIELD_PASSKEY: self.passkey}
    
    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '00:11:22:33:44:55'},
                cls.FIELD_PASSKEY: {'type': 'string', 'nullable': True, 'example': '1234'},
            },
            'required': [cls.FIELD_ADDRESS],
        }
