from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='MemUsage')


@dataclass
class MemUsage(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

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

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    total: Optional[int]
    free: Optional[int]
    used: Optional[int]
    available: Optional[int]
    buff_cache: Optional[int]
    shared: Optional[int]
    swap_total: Optional[int]
    swap_free: Optional[int]
    swap_used: Optional[int]
    sum_total: Optional[int]
    sum_free: Optional[int]
    sum_used: Optional[int]

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> MemUsage:
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
            self.FIELD_SUM_USED: self.sum_used
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_TOTAL: {'type': ['integer', 'null'], 'example': 3981},
                cls.FIELD_FREE: {'type': ['integer', 'null'], 'example': 1335},
                cls.FIELD_USED: {'type': ['integer', 'null'], 'example': 1773},
                cls.FIELD_AVAILABLE: {'type': ['integer', 'null'], 'example': 2207},
                cls.FIELD_BUFF_CACHE: {'type': ['integer', 'null'], 'example': 995},
                cls.FIELD_SHARED: {'type': ['integer', 'null'], 'example': 31},
                cls.FIELD_SWAP_TOTAL: {'type': ['integer', 'null'], 'example': 2147},
                cls.FIELD_SWAP_FREE: {'type': ['integer', 'null'], 'example': 2147},
                cls.FIELD_SWAP_USED: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_SUM_TOTAL: {'type': ['integer', 'null'], 'example': 6128},
                cls.FIELD_SUM_FREE: {'type': ['integer', 'null'], 'example': 3482},
                cls.FIELD_SUM_USED: {'type': ['integer', 'null'], 'example': 1773},
            },
            'required': [],
            'additionalProperties': False,
        }