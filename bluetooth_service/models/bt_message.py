from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from bluetooth_service.models._conversion import bytes_from_list, bytes_to_list, datetime_from_str, datetime_to_str


@dataclass
class BtMessage(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_MESSAGE: ClassVar[str] = 'message'
    FIELD_BYTES: ClassVar[str] = 'bytes'
    FIELD_ISSUED_AT: ClassVar[str] = 'issued_at'
    FIELD_FROM: ClassVar[str] = 'from'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    message: Optional[str] = None
    bytes: Optional[bytes] = None
    issued_at: datetime = field(default_factory=datetime.now)
    from_device: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtMessage:
        return cls(
            message=d.get(cls.FIELD_MESSAGE),
            bytes=bytes_from_list(d.get(cls.FIELD_BYTES)),
            issued_at=datetime_from_str(d.get(cls.FIELD_ISSUED_AT)) or datetime.now(),
            from_device=d.get(cls.FIELD_FROM),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_MESSAGE: self.message,
            self.FIELD_BYTES: bytes_to_list(self.bytes),
            self.FIELD_ISSUED_AT: datetime_to_str(self.issued_at),
            self.FIELD_FROM: self.from_device,
        }

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def payload(self) -> bytes:
        if self.bytes is not None:
            return self.bytes
        if self.message is not None:
            return self.message.encode('utf-8')

        return b''

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_MESSAGE: {'type': 'string', 'nullable': True, 'example': 'AT+VERSION?'},
                cls.FIELD_BYTES: {
                    'type': 'array',
                    'items': {'type': 'integer', 'minimum': 0, 'maximum': 255},
                    'nullable': True,
                    'example': [65, 84, 13, 10],
                },
                cls.FIELD_ISSUED_AT: {'type': 'string', 'example': '2026-04-30T12:00:00'},
                cls.FIELD_FROM: {'type': 'string', 'nullable': True, 'example': '00:11:22:33:44:55'},
            },
            'required': [],
        }
