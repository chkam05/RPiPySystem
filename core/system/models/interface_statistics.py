from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from core.system.enums.interface_channel import InterfaceChannel


@dataclass
class InterfaceStatistics(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_CHANNEL: ClassVar[str] = 'channel'
    FIELD_PACKETS: ClassVar[str] = 'packets'
    FIELD_BYTES: ClassVar[str] = 'bytes'
    FIELD_ERRORS: ClassVar[str] = 'errors'
    FIELD_DROPPED: ClassVar[str] = 'dropped'
    FIELD_OVERRUNS: ClassVar[str] = 'overruns'
    FIELD_FRAME: ClassVar[str] = 'frame'
    FIELD_CARRIER: ClassVar[str] = 'carrier'
    FIELD_COLLISIONS: ClassVar[str] = 'collisions'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    channel: InterfaceChannel
    packets: Optional[int] = None
    bytes: Optional[int] = None
    errors: Optional[int] = None
    dropped: Optional[int] = None
    overruns: Optional[int] = None
    frame: Optional[int] = None
    carrier: Optional[int] = None
    collisions: Optional[int] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> InterfaceStatistics:
        return cls(
            channel=InterfaceChannel.from_str(d[cls.FIELD_CHANNEL]),
            packets=d.get(cls.FIELD_PACKETS),
            bytes=d.get(cls.FIELD_BYTES),
            errors=d.get(cls.FIELD_ERRORS),
            dropped=d.get(cls.FIELD_DROPPED),
            overruns=d.get(cls.FIELD_OVERRUNS),
            frame=d.get(cls.FIELD_FRAME),
            carrier=d.get(cls.FIELD_CARRIER),
            collisions=d.get(cls.FIELD_COLLISIONS),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_CHANNEL: self.channel.value,
            self.FIELD_PACKETS: self.packets,
            self.FIELD_BYTES: self.bytes,
            self.FIELD_ERRORS: self.errors,
            self.FIELD_DROPPED: self.dropped,
            self.FIELD_OVERRUNS: self.overruns,
            self.FIELD_FRAME: self.frame,
            self.FIELD_CARRIER: self.carrier,
            self.FIELD_COLLISIONS: self.collisions,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CHANNEL: {'type': 'string', 'enum': InterfaceChannel.get_all_str(), 'example': InterfaceChannel.RX.value, 'description': 'Traffic channel direction.'},
                cls.FIELD_PACKETS: {'type': 'integer', 'nullable': True, 'example': 1024, 'description': 'Packet count.'},
                cls.FIELD_BYTES: {'type': 'integer', 'nullable': True, 'example': 1048576, 'description': 'Byte count.'},
                cls.FIELD_ERRORS: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Error count.'},
                cls.FIELD_DROPPED: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Dropped packet count.'},
                cls.FIELD_OVERRUNS: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Overrun count.'},
                cls.FIELD_FRAME: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Frame error count.'},
                cls.FIELD_CARRIER: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Carrier error count.'},
                cls.FIELD_COLLISIONS: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Collision count.'},
            },
            'required': [cls.FIELD_CHANNEL],
        }
