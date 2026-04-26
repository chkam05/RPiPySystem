from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional


@dataclass
class BluetoothMessageRecord:
    # --- Field-name constants ---
    FIELD_SEND_MESSAGE: ClassVar[str] = 'send_message'
    FIELD_SEND_BYTES: ClassVar[str] = 'send_bytes'
    FIELD_SEND_AT: ClassVar[str] = 'send_at'
    FIELD_RECEIVED_MESSAGE: ClassVar[str] = 'received_message'
    FIELD_RECEIVED_BYTES: ClassVar[str] = 'received_bytes'
    FIELD_RECEIVED_AT: ClassVar[str] = 'received_at'

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    # --- Fields ---
    send_message: Optional[str] = None
    send_bytes: Optional[bytes] = None
    send_at: Optional[datetime] = None

    received_message: Optional[str] = None
    received_bytes: Optional[bytes] = None
    received_at: Optional[datetime] = None
    
    # --- Packaging methods ---

    @staticmethod
    def _bytes_to_list(data: Optional[bytes]) -> Optional[List[int]]:
        """
        Convert bytes to list of ints.
        """
        if data is None:
            return None
        return list(data)

    @staticmethod
    def _list_to_bytes(data: Optional[List[int]]) -> Optional[bytes]:
        """
        Convert list of ints to bytes.
        """
        if data is None:
            return None
        return bytes(data)

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
    def from_dict(cls, data: Dict[str, Any]) -> 'BluetoothMessageRecord':
        return cls(
            send_message=data.get(cls.FIELD_SEND_MESSAGE),
            send_bytes=cls._list_to_bytes(data.get(cls.FIELD_SEND_BYTES)),
            send_at=cls._str_to_dt(data.get(cls.FIELD_SEND_AT)),
            received_message=data.get(cls.FIELD_RECEIVED_MESSAGE),
            received_bytes=cls._list_to_bytes(data.get(cls.FIELD_RECEIVED_BYTES)),
            received_at=cls._str_to_dt(data.get(cls.FIELD_RECEIVED_AT)),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_SEND_MESSAGE: self.send_message,
            self.FIELD_SEND_BYTES: self._bytes_to_list(self.send_bytes),
            self.FIELD_SEND_AT: self._dt_to_str(self.send_at),
            self.FIELD_RECEIVED_MESSAGE: self.received_message,
            self.FIELD_RECEIVED_BYTES: self._bytes_to_list(self.received_bytes),
            self.FIELD_RECEIVED_AT: self._dt_to_str(self.received_at)
        }
    
    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, items: List[Dict[str, Any]]) -> List['BluetoothMessageRecord']:
        return [cls.from_dict(item) for item in items]

    @classmethod
    def list_to_public(cls, items: List['BluetoothMessageRecord']) -> List[Dict[str, Any]]:
        return [item.to_public() for item in items]

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_SEND_MESSAGE: {'type': 'string', 'nullable': True, 'example': 'AT+VERSION?'},
                cls.FIELD_SEND_BYTES: {
                    'type': 'array',
                    'items': {'type': 'integer', 'minimum': 0, 'maximum': 255},
                    'nullable': True,
                    'example': [0x01, 0x02, 0x03],
                },
                cls.FIELD_SEND_AT: {'type': 'string', 'nullable': True, 'example': '2025-01-01 12:00:00'},
                cls.FIELD_RECEIVED_MESSAGE: {'type': 'string', 'nullable': True, 'example': 'OK'},
                cls.FIELD_RECEIVED_BYTES: {
                    'type': 'array',
                    'items': {'type': 'integer', 'minimum': 0, 'maximum': 255},
                    'nullable': True,
                    'example': [0x4F, 0x4B],
                },
                cls.FIELD_RECEIVED_AT: {'type': 'string', 'nullable': True, 'example': '2025-01-01 12:00:01'},
            },
        }

    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }

    @classmethod
    def schema_add_request(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_SEND_MESSAGE: {'type': 'string', 'nullable': True, 'example': 'AT+VERSION?'},
                cls.FIELD_SEND_BYTES: {
                    'type': 'array',
                    'items': {'type': 'integer', 'minimum': 0, 'maximum': 255},
                    'nullable': True,
                    'example': [0x01, 0x02, 0x03],
                },
            },
            'required': [],
        }