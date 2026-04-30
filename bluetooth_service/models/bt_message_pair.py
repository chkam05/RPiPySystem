from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from bluetooth_service.models.bt_message import BtMessage


@dataclass
class BtMessagePair(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_SEND: ClassVar[str] = 'send'
    FIELD_RECEIVED: ClassVar[str] = 'received'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    send: BtMessage
    received: Optional[BtMessage] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BtMessagePair:
        return cls(
            send=BtMessage.from_dict(d[cls.FIELD_SEND]),
            received=BtMessage.from_dict(d[cls.FIELD_RECEIVED]) if d.get(cls.FIELD_RECEIVED) else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_SEND: self.send.to_public(),
            self.FIELD_RECEIVED: self.received.to_public() if self.received else None,
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_SEND: BtMessage.schema_public(),
                cls.FIELD_RECEIVED: {**BtMessage.schema_public(), 'nullable': True},
            },
            'required': [cls.FIELD_SEND],
        }
