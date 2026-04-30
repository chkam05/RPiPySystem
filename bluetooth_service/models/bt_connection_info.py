from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from bluetooth_service.models._conversion import datetime_from_str, datetime_to_str


@dataclass
class BtConnectionInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_CONNECTION_ID: ClassVar[str] = 'connection_id'
    FIELD_ADDRESS: ClassVar[str] = 'address'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_PORT: ClassVar[str] = 'port'
    FIELD_CREATED_AT: ClassVar[str] = 'created_at'
    FIELD_LAST_USED_AT: ClassVar[str] = 'last_used_at'
    FIELD_CONNECTED: ClassVar[str] = 'connected'
    FIELD_RECEIVED_COUNT: ClassVar[str] = 'received_count'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    connection_id: str
    address: str
    name: Optional[str] = None
    port: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    connected: bool = True
    received_count: int = 0

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtConnectionInfo:
        return cls(
            connection_id=d[cls.FIELD_CONNECTION_ID],
            address=d[cls.FIELD_ADDRESS],
            name=d.get(cls.FIELD_NAME),
            port=int(d.get(cls.FIELD_PORT, 1)),
            created_at=datetime_from_str(d.get(cls.FIELD_CREATED_AT)) or datetime.now(),
            last_used_at=datetime_from_str(d.get(cls.FIELD_LAST_USED_AT)),
            connected=bool(d.get(cls.FIELD_CONNECTED, True)),
            received_count=int(d.get(cls.FIELD_RECEIVED_COUNT, 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_CONNECTION_ID: self.connection_id,
            self.FIELD_ADDRESS: self.address,
            self.FIELD_NAME: self.name,
            self.FIELD_PORT: self.port,
            self.FIELD_CREATED_AT: datetime_to_str(self.created_at),
            self.FIELD_LAST_USED_AT: datetime_to_str(self.last_used_at),
            self.FIELD_CONNECTED: self.connected,
            self.FIELD_RECEIVED_COUNT: self.received_count,
        }

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def touch(self) -> None:
        self.last_used_at = datetime.now()

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CONNECTION_ID: {'type': 'string', 'example': 'hc05'},
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '00:11:22:33:44:55'},
                cls.FIELD_NAME: {'type': 'string', 'nullable': True, 'example': 'HC-05'},
                cls.FIELD_PORT: {'type': 'integer', 'example': 1},
                cls.FIELD_CREATED_AT: {'type': 'string', 'example': '2026-04-30T12:00:00'},
                cls.FIELD_LAST_USED_AT: {'type': 'string', 'nullable': True, 'example': '2026-04-30T12:01:00'},
                cls.FIELD_CONNECTED: {'type': 'boolean', 'example': True},
                cls.FIELD_RECEIVED_COUNT: {'type': 'integer', 'example': 2},
            },
            'required': [cls.FIELD_CONNECTION_ID, cls.FIELD_ADDRESS, cls.FIELD_CONNECTED],
        }
