from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

from system_service.models.internal.interface_channel import InterfaceChannel


@dataclass
class InterfaceStatistics:
    # --- Field-name constants ---
    FIELD_CHANNEL: ClassVar[str] = 'channel'
    FIELD_PACKETS: ClassVar[str] = 'packets'
    FIELD_BYTES: ClassVar[str] = 'bytes'
    FIELD_ERRORS: ClassVar[str] = 'errors'
    FIELD_DROPPED: ClassVar[str] = 'dropped'
    FIELD_OVERRUNS: ClassVar[str] = 'overruns'
    FIELD_FRAME: ClassVar[str] = 'frame'
    FIELD_CARRIER: ClassVar[str] = 'carrier'
    FIELD_COLLISIONS: ClassVar[str] = 'collisions'

    # --- Fields ---
    channel: InterfaceChannel
    
    packets: Optional[int] = None
    bytes: Optional[int] = None
    errors: Optional[int] = None
    dropped: Optional[int] = None
    overruns: Optional[int] = None
    frame: Optional[int] = None
    carrier: Optional[int] = None
    collisions: Optional[int] = None

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'InterfaceStatistics':
        ch = d.get(cls.FIELD_CHANNEL, 'RX')

        return cls(
            channel=InterfaceChannel.from_str(ch),
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
            self.FIELD_CHANNEL: str(self.channel),
            self.FIELD_PACKETS: self.packets,
            self.FIELD_BYTES: self.bytes,
            self.FIELD_ERRORS: self.errors,
            self.FIELD_DROPPED: self.dropped,
            self.FIELD_OVERRUNS: self.overruns,
            self.FIELD_FRAME: self.frame,
            self.FIELD_CARRIER: self.carrier,
            self.FIELD_COLLISIONS: self.collisions,
        }
    
    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, rows: List[Dict[str, Any]]) -> List['InterfaceStatistics']:
        return [cls.from_dict(r) for r in (rows or [])]

    @staticmethod
    def list_to_public(items: List['InterfaceStatistics']) -> List[Dict[str, Any]]:
        return [i.to_public() for i in (items or [])]
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        channel_values = InterfaceChannel.get_all_str()

        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CHANNEL: {'type': 'string', 'enum': channel_values, 'example': 'RX'},
                cls.FIELD_PACKETS: {'type': 'integer', 'example': 60471},
                cls.FIELD_BYTES: {'type': 'integer', 'example': 11234805},
                cls.FIELD_ERRORS: {'type': 'integer', 'example': 0},
                cls.FIELD_DROPPED: {'type': 'integer', 'example': 4},
                cls.FIELD_OVERRUNS: {'type': 'integer', 'example': 0},
                cls.FIELD_FRAME: {'type': 'integer', 'example': 0},
                cls.FIELD_CARRIER: {'type': 'integer', 'example': 0},
                cls.FIELD_COLLISIONS: {'type': 'integer', 'example': 0},
            },
            'required': [cls.FIELD_CHANNEL],
            'additionalProperties': False,
        }

    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }