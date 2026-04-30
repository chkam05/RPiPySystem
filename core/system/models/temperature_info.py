from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class TemperatureInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_MAX_TEMP_C: ClassVar[str] = 'max_temp_c'
    FIELD_TEMP_C: ClassVar[str] = 'temp_c'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    max_temp_c: Optional[float] = None
    temp_c: Optional[float] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> TemperatureInfo:
        return cls(
            max_temp_c=d.get(cls.FIELD_MAX_TEMP_C),
            temp_c=d.get(cls.FIELD_TEMP_C)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_MAX_TEMP_C: self.max_temp_c,
            self.FIELD_TEMP_C: self.temp_c
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_MAX_TEMP_C: {'type': 'number', 'nullable': True, 'example': 85.0, 'description': 'Critical or hot temperature threshold in Celsius.'},
                cls.FIELD_TEMP_C: {'type': 'number', 'nullable': True, 'example': 42.5, 'description': 'Current primary temperature in Celsius.'},
            },
            'required': [],
        }
