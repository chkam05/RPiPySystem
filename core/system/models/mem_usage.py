from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class MemUsage(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_TOTAL: ClassVar[str] = 'total'
    FIELD_FREE: ClassVar[str] = 'free'
    FIELD_USED: ClassVar[str] = 'used'
    FIELD_AVAILABLE: ClassVar[str] = 'available'
    FIELD_BUFF_CACHE: ClassVar[str] = 'buff_cache'
    FIELD_SHARED: ClassVar[str] = 'shared'
    FIELD_SWAP_TOTAL: ClassVar[str] = 'swap_total'
    FIELD_SWAP_FREE: ClassVar[str] = 'swap_free'
    FIELD_SWAP_USED: ClassVar[str] = 'swap_used'
    FIELD_SUM_TOTAL: ClassVar[str] = 'sum_total'
    FIELD_SUM_FREE: ClassVar[str] = 'sum_free'
    FIELD_SUM_USED: ClassVar[str] = 'sum_used'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    total: Optional[int] = None
    free: Optional[int] = None
    used: Optional[int] = None
    available: Optional[int] = None
    buff_cache: Optional[int] = None
    shared: Optional[int] = None
    swap_total: Optional[int] = None
    swap_free: Optional[int] = None
    swap_used: Optional[int] = None
    sum_total: Optional[int] = None
    sum_free: Optional[int] = None
    sum_used: Optional[int] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> MemUsage:
        return cls(
            total=d.get(cls.FIELD_TOTAL),
            free=d.get(cls.FIELD_FREE),
            used=d.get(cls.FIELD_USED),
            available=d.get(cls.FIELD_AVAILABLE),
            buff_cache=d.get(cls.FIELD_BUFF_CACHE),
            shared=d.get(cls.FIELD_SHARED),
            swap_total=d.get(cls.FIELD_SWAP_TOTAL),
            swap_free=d.get(cls.FIELD_SWAP_FREE),
            swap_used=d.get(cls.FIELD_SWAP_USED),
            sum_total=d.get(cls.FIELD_SUM_TOTAL),
            sum_free=d.get(cls.FIELD_SUM_FREE),
            sum_used=d.get(cls.FIELD_SUM_USED),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_TOTAL: self.total,
            self.FIELD_FREE: self.free,
            self.FIELD_USED: self.used,
            self.FIELD_AVAILABLE: self.available,
            self.FIELD_BUFF_CACHE: self.buff_cache,
            self.FIELD_SHARED: self.shared,
            self.FIELD_SWAP_TOTAL: self.swap_total,
            self.FIELD_SWAP_FREE: self.swap_free,
            self.FIELD_SWAP_USED: self.swap_used,
            self.FIELD_SUM_TOTAL: self.sum_total,
            self.FIELD_SUM_FREE: self.sum_free,
            self.FIELD_SUM_USED: self.sum_used,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_TOTAL: {'type': 'integer', 'nullable': True, 'example': 3796, 'description': 'Total RAM memory in MB.'},
                cls.FIELD_FREE: {'type': 'integer', 'nullable': True, 'example': 168, 'description': 'Free RAM memory in MB.'},
                cls.FIELD_USED: {'type': 'integer', 'nullable': True, 'example': 2437, 'description': 'Used RAM memory in MB.'},
                cls.FIELD_AVAILABLE: {'type': 'integer', 'nullable': True, 'example': 1211, 'description': 'Available RAM memory in MB.'},
                cls.FIELD_BUFF_CACHE: {'type': 'integer', 'nullable': True, 'example': 1191, 'description': 'Buffers and cache memory in MB.'},
                cls.FIELD_SHARED: {'type': 'integer', 'nullable': True, 'example': 30, 'description': 'Shared memory in MB.'},
                cls.FIELD_SWAP_TOTAL: {'type': 'integer', 'nullable': True, 'example': 2047, 'description': 'Total swap memory in MB.'},
                cls.FIELD_SWAP_FREE: {'type': 'integer', 'nullable': True, 'example': 2047, 'description': 'Free swap memory in MB.'},
                cls.FIELD_SWAP_USED: {'type': 'integer', 'nullable': True, 'example': 0, 'description': 'Used swap memory in MB.'},
                cls.FIELD_SUM_TOTAL: {'type': 'integer', 'nullable': True, 'example': 5843, 'description': 'Total RAM and swap memory in MB.'},
                cls.FIELD_SUM_FREE: {'type': 'integer', 'nullable': True, 'example': 2215, 'description': 'Free RAM and swap memory in MB.'},
                cls.FIELD_SUM_USED: {'type': 'integer', 'nullable': True, 'example': 2437, 'description': 'Used RAM and swap memory in MB.'},
            },
            'required': [],
        }
