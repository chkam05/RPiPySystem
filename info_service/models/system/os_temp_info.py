from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional


@dataclass
class OSTempInfo:
    # --- Field-name constants ---
    FIELD_MAX_TEMP_C: ClassVar[str] = 'max_temp_c'
    FIELD_TEMP_C: ClassVar[str] = 'temp_c'

    # --- Fields ---
    max_temp_c: Optional[float]
    temp_c: Optional[float]

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'OSTempInfo':
        return cls(
            max_temp_c=d.get(cls.FIELD_MAX_TEMP_C),
            temp_c=d.get(cls.FIELD_TEMP_C)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_MAX_TEMP_C: self.max_temp_c,
            self.FIELD_TEMP_C: self.temp_c
        }

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Schema methods ---

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