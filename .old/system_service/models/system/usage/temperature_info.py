from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='TemperatureInfo')


@dataclass
class TemperatureInfo(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_MAX_TEMP_C: ClassVar[str] = 'max_temp_c'
    FIELD_TEMP_C: ClassVar[str] = 'temp_c'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    max_temp_c: Optional[float]
    temp_c: Optional[float]

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> TemperatureInfo:
        return cls(
            max_temp_c=d.get(cls.FIELD_MAX_TEMP_C),
            temp_c=d.get(cls.FIELD_TEMP_C)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_MAX_TEMP_C: self.max_temp_c,
            self.FIELD_TEMP_C: self.temp_c
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_MAX_TEMP_C: {'type': ['number', 'null'], 'example': 90},
                cls.FIELD_TEMP_C: {'type': ['number', 'null'], 'example': 52.3}
            },
            'required': [],
            'additionalProperties': False,
        }