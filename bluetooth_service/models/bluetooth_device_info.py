from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional


@dataclass
class BluetoothDeviceInfo:
    # --- Field-name constants ---
    FIELD_ADDRESS: ClassVar[str] = 'address'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_ALIAS: ClassVar[str] = 'alias'
    FIELD_PAIRED: ClassVar[str] = 'paired'
    FIELD_TRUSTED: ClassVar[str] = 'trusted'
    FIELD_CONNECTED: ClassVar[str] = 'connected'
    FIELD_BLOCKED: ClassVar[str] = 'blocked'
    FIELD_RSSI: ClassVar[str] = 'rssi'
    FIELD_MANUFACTURER_ID: ClassVar[str] = 'manufacturer_id'
    FIELD_MANUFACTURER_SPEC_DATA: ClassVar[str] = 'manufacturer_spec_data'
    FIELD_UUIDS: ClassVar[str] = 'uuids'
    FIELD_LAST_SEEN: ClassVar[str] = 'last_seen'

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    # --- Fields ---
    address: str
    name: Optional[str] = None
    alias: Optional[str] = None
    paired: bool = False
    trusted: bool = False
    connected: bool = False
    blocked: bool = False
    rssi: Optional[int] = None
    manufacturer_id: Optional[int] = None
    manufacturer_spec_data: Optional[List[int]] = field(default_factory=list)
    uuids: List[str] = field(default_factory=list)
    last_seen: Optional[datetime] = None

    # --- Packaging methods ---

    @classmethod
    def _dt_to_str(cls, dt: Optional[datetime]) -> Optional[str]:
        """
        Convert datetime to string.
        """
        if dt is None:
            return None
        return dt.strftime(cls.DATETIME_FORMAT)

    @classmethod
    def _str_to_dt(cls, value: Optional[str]) -> Optional[datetime]:
        """
        Convert string to datetime.
        """
        if not value:
            return None
        return datetime.strptime(value, cls.DATETIME_FORMAT)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BluetoothDeviceInfo':
        return cls(
            address=data[cls.FIELD_ADDRESS],
            name=data.get(cls.FIELD_NAME),
            alias=data.get(cls.FIELD_ALIAS),
            paired=bool(data.get(cls.FIELD_PAIRED, False)),
            trusted=bool(data.get(cls.FIELD_TRUSTED, False)),
            connected=bool(data.get(cls.FIELD_CONNECTED, False)),
            blocked=bool(data.get(cls.FIELD_BLOCKED, False)),
            rssi=data.get(cls.FIELD_RSSI),
            manufacturer_id=data.get(cls.FIELD_MANUFACTURER_ID),
            manufacturer_spec_data=data.get(cls.FIELD_MANUFACTURER_SPEC_DATA, []),
            uuids=data.get(cls.FIELD_UUIDS, []),
            last_seen=cls._str_to_dt(data.get(cls.FIELD_LAST_SEEN)),
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
            self.FIELD_MANUFACTURER_ID: self.manufacturer_id,
            self.FIELD_MANUFACTURER_SPEC_DATA: self.manufacturer_spec_data,
            self.FIELD_UUIDS: self.uuids,
            self.FIELD_LAST_SEEN: self._dt_to_str(self.last_seen),
        }

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, items: List[Dict[str, Any]]) -> List['BluetoothDeviceInfo']:
        return [cls.from_dict(item) for item in items]

    @classmethod
    def list_to_public(cls, items: List['BluetoothDeviceInfo']) -> List[Dict[str, Any]]:
        return [item.to_public() for item in items]

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '00:11:22:33:44:55'},
                cls.FIELD_NAME: {'type': 'string', 'nullable': True, 'example': 'HC-05'},
                cls.FIELD_ALIAS: {'type': 'string', 'nullable': True, 'example': 'My HC-05'},
                cls.FIELD_PAIRED: {'type': 'boolean', 'example': True},
                cls.FIELD_TRUSTED: {'type': 'boolean', 'example': True},
                cls.FIELD_CONNECTED: {'type': 'boolean', 'example': False},
                cls.FIELD_BLOCKED: {'type': 'boolean', 'example': False},
                cls.FIELD_RSSI: {'type': 'integer', 'nullable': True, 'example': -60},
                cls.FIELD_MANUFACTURER_ID: {'type': 'integer', 'nullable': True, 'example': '64'},
                cls.FIELD_MANUFACTURER_SPEC_DATA: {'type': 'array', 'items': {'type': 'integer'}, 'example': [1, 0, 2, 0, 1, 3]},
                cls.FIELD_UUIDS: {'type': 'array', 'items': {'type': 'string'}, 'example': ['00001101-0000-1000-8000-00805F9B34FB']},
                cls.FIELD_LAST_SEEN: {'type': 'string', 'nullable': True, 'example': '2025-01-01 12:00:00'},
            },
            'required': [
                cls.FIELD_ADDRESS,
            ],
        }

    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }