from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional


@dataclass
class BluetoothConnectionInfo:
    # --- Field-name constants ---
    FIELD_CONNECTION_ID: ClassVar[str] = 'connection_id'
    FIELD_ADDRESS: ClassVar[str] = 'address'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_PORT: ClassVar[str] = 'port'
    FIELD_CREATED_AT: ClassVar[str] = 'created_at'
    FIELD_LAST_USED_AT: ClassVar[str] = 'last_used_at'
    FIELD_IS_CONNECTED: ClassVar[str] = 'is_connected'

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    # --- Fields ---
    connection_id: str  # e.g. name or MAC
    address: str
    name: Optional[str] = None
    port: Optional[int] = None
    created_at: datetime = datetime.now
    last_used_at: Optional[datetime] = None
    is_connected: bool = True

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

    def touch(self) -> None:
        """
        Update last_used_at to now.
        """
        self.last_used_at = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BluetoothConnectionInfo':
        return cls(
            connection_id=data[cls.FIELD_CONNECTION_ID],
            address=data[cls.FIELD_ADDRESS],
            name=data.get(cls.FIELD_NAME),
            port=data.get(cls.FIELD_PORT),
            created_at=cls._str_to_dt(data.get(cls.FIELD_CREATED_AT)) or datetime.now(),
            last_used_at=cls._str_to_dt(data.get(cls.FIELD_LAST_USED_AT)),
            is_connected=bool(data.get(cls.FIELD_IS_CONNECTED, True)),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_CONNECTION_ID: self.connection_id,
            self.FIELD_ADDRESS: self.address,
            self.FIELD_NAME: self.name,
            self.FIELD_PORT: self.port,
            self.FIELD_CREATED_AT: self._dt_to_str(self.created_at),
            self.FIELD_LAST_USED_AT: self._dt_to_str(self.last_used_at),
            self.FIELD_IS_CONNECTED: self.is_connected,
        }

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, items: List[Dict[str, Any]]) -> List['BluetoothConnectionInfo']:
        return [cls.from_dict(item) for item in items]

    @classmethod
    def list_to_public(cls, items: List['BluetoothConnectionInfo']) -> List[Dict[str, Any]]:
        return [item.to_public() for item in items]

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CONNECTION_ID: {'type': 'string', 'example': 'HC-05'},
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '00:11:22:33:44:55'},
                cls.FIELD_NAME: {'type': 'string', 'nullable': True, 'example': 'HC-05'},
                cls.FIELD_PORT: {'type': 'integer', 'nullable': True, 'example': 1},
                cls.FIELD_CREATED_AT: {'type': 'string', 'example': '2025-01-01 12:00:00'},
                cls.FIELD_LAST_USED_AT: {'type': 'string', 'nullable': True, 'example': '2025-01-01 12:05:00'},
                cls.FIELD_IS_CONNECTED: {'type': 'boolean', 'example': True},
            },
            'required': [
                cls.FIELD_CONNECTION_ID,
                cls.FIELD_ADDRESS,
                cls.FIELD_IS_CONNECTED,
            ],
        }

    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }