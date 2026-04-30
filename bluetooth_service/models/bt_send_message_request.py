from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from bluetooth_service.exceptions.bluetooth_service_error import BluetoothServiceError
from core.data.public_data_model import PublicDataModel
from bluetooth_service.models._conversion import bytes_from_list, bytes_to_list
from bluetooth_service.models.bt_message import BtMessage


@dataclass
class BtSendMessageRequest(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------
    
    FIELD_MESSAGE: ClassVar[str] = 'message'
    FIELD_BYTES: ClassVar[str] = 'bytes'
    FIELD_TIMEOUT: ClassVar[str] = 'timeout'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    message: Optional[str] = None
    bytes: Optional[bytes] = None
    timeout: float = 5.0

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtSendMessageRequest:
        return cls(
            message=d.get(cls.FIELD_MESSAGE),
            bytes=bytes_from_list(d.get(cls.FIELD_BYTES)),
            timeout=float(d.get(cls.FIELD_TIMEOUT, 5.0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_MESSAGE: self.message,
            self.FIELD_BYTES: bytes_to_list(self.bytes),
            self.FIELD_TIMEOUT: self.timeout,
        }

    def to_message(self, from_device: str | None = None) -> BtMessage:
        self._validate_payload()
        return BtMessage(message=self.message, bytes=self.bytes, from_device=from_device)

    # --------------------------------------------------------------------------------
    # UTILITIES
    # --------------------------------------------------------------------------------

    def _validate_payload(self) -> None:
        has_message = self.message is not None and self.message != ''
        has_bytes = self.bytes is not None and len(self.bytes) > 0
        if has_message == has_bytes:
            raise BluetoothServiceError('Request must contain exactly one payload field: "message" or "bytes".')

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_MESSAGE: {'type': 'string', 'nullable': True, 'example': 'ping\\n'},
                cls.FIELD_BYTES: {
                    'type': 'array',
                    'items': {'type': 'integer', 'minimum': 0, 'maximum': 255},
                    'nullable': True,
                    'example': [112, 105, 110, 103, 10],
                },
                cls.FIELD_TIMEOUT: {'type': 'number', 'example': 5.0},
            },
            'required': [],
            'description': 'Provide exactly one payload field: message or bytes.',
        }
