from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='CPUUsage')


@dataclass
class CPUUsage(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_CORES: ClassVar[str] = 'cores'
    FIELD_TOTAL: ClassVar[str] = 'total'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    cores: Dict[str, float]     # {'cpu0': 3.4, 'cpu1': 7.9, ...} in %
    total: Optional[float]      # in %

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> CPUUsage:
        return cls(
            cores=d.get(cls.FIELD_CORES, {}) or {},
            total=d.get(cls.FIELD_TOTAL)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_CORES: self.cores,
            self.FIELD_TOTAL: self.total,
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CORES: {
                    'type': 'object',
                    'additionalProperties': {'type': 'number'},
                    'example': {'cpu0': 8.1, 'cpu1': 16.9}
                },
                cls.FIELD_TOTAL: {'type': ['number', 'null'], 'example': 12.5},
            },
            'required': [],
            'additionalProperties': False,
        }