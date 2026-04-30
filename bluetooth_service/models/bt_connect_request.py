from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class BtConnectRequest(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_ADDRESS: ClassVar[str] = 'address'
    FIELD_PORT: ClassVar[str] = 'port'
    FIELD_CONNECTION_ID: ClassVar[str] = 'connection_id'
    FIELD_NAME: ClassVar[str] = 'name'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    address: str
    port: int = 1
    connection_id: Optional[str] = None
    name: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtConnectRequest:
        return cls(
            address=str(d[cls.FIELD_ADDRESS]),
            port=int(d.get(cls.FIELD_PORT, 1)),
            connection_id=d.get(cls.FIELD_CONNECTION_ID),
            name=d.get(cls.FIELD_NAME),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_ADDRESS: self.address,
            self.FIELD_PORT: self.port,
            self.FIELD_CONNECTION_ID: self.connection_id,
            self.FIELD_NAME: self.name,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '00:11:22:33:44:55'},
                cls.FIELD_PORT: {'type': 'integer', 'example': 1},
                cls.FIELD_CONNECTION_ID: {'type': 'string', 'nullable': True, 'example': 'hc05'},
                cls.FIELD_NAME: {'type': 'string', 'nullable': True, 'example': 'HC-05'},
            },
            'required': [cls.FIELD_ADDRESS],
        }
