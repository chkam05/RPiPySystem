from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class CPUInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_MODEL: ClassVar[str] = 'model'
    FIELD_ARCHITECTURE: ClassVar[str] = 'architecture'
    FIELD_CORES_LOGICAL: ClassVar[str] = 'cores_logical'
    FIELD_CORES_PHYSICAL: ClassVar[str] = 'cores_physical'
    FIELD_FREQ: ClassVar[str] = 'freq'
    FIELD_FREQ_MIN: ClassVar[str] = 'freq_min'
    FIELD_FREQ_MAX: ClassVar[str] = 'freq_max'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    model: Optional[str] = None
    architecture: Optional[str] = None
    cores_logical: Optional[int] = None
    cores_physical: Optional[int] = None
    freq: Optional[float] = None
    freq_min: Optional[float] = None
    freq_max: Optional[float] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CPUInfo:
        return cls(
            model=d.get(cls.FIELD_MODEL),
            architecture=d.get(cls.FIELD_ARCHITECTURE),
            cores_logical=d.get(cls.FIELD_CORES_LOGICAL),
            cores_physical=d.get(cls.FIELD_CORES_PHYSICAL),
            freq=d.get(cls.FIELD_FREQ),
            freq_min=d.get(cls.FIELD_FREQ_MIN),
            freq_max=d.get(cls.FIELD_FREQ_MAX),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_MODEL: self.model,
            self.FIELD_ARCHITECTURE: self.architecture,
            self.FIELD_CORES_LOGICAL: self.cores_logical,
            self.FIELD_CORES_PHYSICAL: self.cores_physical,
            self.FIELD_FREQ: self.freq,
            self.FIELD_FREQ_MIN: self.freq_min,
            self.FIELD_FREQ_MAX: self.freq_max,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_MODEL: {'type': 'string', 'nullable': True, 'example': 'ARM Cortex-A72', 'description': 'CPU model name.'},
                cls.FIELD_ARCHITECTURE: {'type': 'string', 'nullable': True, 'example': 'aarch64', 'description': 'CPU architecture.'},
                cls.FIELD_CORES_LOGICAL: {'type': 'integer', 'nullable': True, 'example': 4, 'description': 'Number of logical CPU cores.'},
                cls.FIELD_CORES_PHYSICAL: {'type': 'integer', 'nullable': True, 'example': 4, 'description': 'Number of physical CPU cores if available.'},
                cls.FIELD_FREQ: {'type': 'number', 'nullable': True, 'example': 1800.0, 'description': 'Current CPU frequency in MHz.'},
                cls.FIELD_FREQ_MIN: {'type': 'number', 'nullable': True, 'example': 600.0, 'description': 'Minimum CPU frequency in MHz.'},
                cls.FIELD_FREQ_MAX: {'type': 'number', 'nullable': True, 'example': 1800.0, 'description': 'Maximum CPU frequency in MHz.'},
            },
            'required': [],
        }
