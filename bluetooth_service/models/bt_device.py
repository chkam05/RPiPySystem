from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from bluetooth_service.models._conversion import datetime_from_str, datetime_to_str


@dataclass
class BtDevice(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_ADDRESS: ClassVar[str] = 'address'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_ALIAS: ClassVar[str] = 'alias'
    FIELD_PAIRED: ClassVar[str] = 'paired'
    FIELD_TRUSTED: ClassVar[str] = 'trusted'
    FIELD_CONNECTED: ClassVar[str] = 'connected'
    FIELD_BLOCKED: ClassVar[str] = 'blocked'
    FIELD_RSSI: ClassVar[str] = 'rssi'
    FIELD_UUIDS: ClassVar[str] = 'uuids'
    FIELD_LAST_SEEN: ClassVar[str] = 'last_seen'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    address: str
    name: Optional[str] = None
    alias: Optional[str] = None
    paired: bool = False
    trusted: bool = False
    connected: bool = False
    blocked: bool = False
    rssi: Optional[int] = None
    uuids: list[str] = field(default_factory=list)
    last_seen: Optional[datetime] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtDevice:
        return cls(
            address=d[cls.FIELD_ADDRESS],
            name=d.get(cls.FIELD_NAME),
            alias=d.get(cls.FIELD_ALIAS),
            paired=bool(d.get(cls.FIELD_PAIRED, False)),
            trusted=bool(d.get(cls.FIELD_TRUSTED, False)),
            connected=bool(d.get(cls.FIELD_CONNECTED, False)),
            blocked=bool(d.get(cls.FIELD_BLOCKED, False)),
            rssi=d.get(cls.FIELD_RSSI),
            uuids=d.get(cls.FIELD_UUIDS, []),
            last_seen=datetime_from_str(d.get(cls.FIELD_LAST_SEEN)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_ADDRESS: self.address,
            self.FIELD_NAME: self.name,
            self.FIELD_ALIAS: self.alias,
            self.FIELD_PAIRED: self.paired,
            self.FIELD_TRUSTED: self.trusted,
            self.FIELD_CONNECTED: self.connected,
            self.FIELD_BLOCKED: self.blocked,
            self.FIELD_RSSI: self.rssi,
            self.FIELD_UUIDS: self.uuids,
            self.FIELD_LAST_SEEN: datetime_to_str(self.last_seen),
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
                cls.FIELD_NAME: {'type': 'string', 'nullable': True, 'example': 'HC-05'},
                cls.FIELD_ALIAS: {'type': 'string', 'nullable': True, 'example': 'Arduino BT'},
                cls.FIELD_PAIRED: {'type': 'boolean', 'example': True},
                cls.FIELD_TRUSTED: {'type': 'boolean', 'example': True},
                cls.FIELD_CONNECTED: {'type': 'boolean', 'example': False},
                cls.FIELD_BLOCKED: {'type': 'boolean', 'example': False},
                cls.FIELD_RSSI: {'type': 'integer', 'nullable': True, 'example': -60},
                cls.FIELD_UUIDS: {'type': 'array', 'items': {'type': 'string'}},
                cls.FIELD_LAST_SEEN: {'type': 'string', 'nullable': True, 'example': '2026-04-30T12:00:00'},
            },
            'required': [cls.FIELD_ADDRESS],
        }
