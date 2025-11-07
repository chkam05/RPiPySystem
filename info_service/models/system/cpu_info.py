from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional


@dataclass
class CPUInfo:
    # --- Field-name constants ---
    FIELD_MODEL: ClassVar[str] = 'model'
    FIELD_ARCHITECTURE: ClassVar[str] = 'architecture'
    FIELD_CORES_LOGICAL: ClassVar[str] = 'cores_logical'
    FIELD_CORES_PHYSICAL: ClassVar[str] = 'cores_physical'
    FIELD_FREQ: ClassVar[str] = 'freq'
    FIELD_FREQ_MIN: ClassVar[str] = 'freq_min'
    FIELD_FREQ_MAX: ClassVar[str] = 'freq_max'

    # --- Fields ---
    model: Optional[str]            # e.g.: 'ARM Cortex-A72'.
    architecture: Optional[str]     # e.g.: 'aarch64'.
    cores_logical: Optional[int]    # Nmber of threads (logical CPUs).
    cores_physical: Optional[int]   # Approximate physical cores (if known).
    freq: Optional[float]           # Current (approximate) single-core clock speed in Mhz.
    freq_min: Optional[float]       # Min single-core clock speed in Mhz.
    freq_max: Optional[float]       # Max single-core clock speed in Mhz.

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CPUInfo':
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
            self.FIELD_FREQ_MAX: self.freq_max
        }

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_MODEL: {'type': ['string', 'null'], 'example': 'ARM Cortex-A72'},
                cls.FIELD_ARCHITECTURE: {'type': ['string', 'null'], 'example': 'aarch64'},
                cls.FIELD_CORES_LOGICAL: {'type': ['integer', 'null'], 'example': 4},
                cls.FIELD_CORES_PHYSICAL: {'type': ['integer', 'null'], 'example': 4},
                cls.FIELD_FREQ: {'type': ['number', 'null'], 'example': 1500.0},
                cls.FIELD_FREQ_MIN: {'type': ['number', 'null'], 'example': 600.0},
                cls.FIELD_FREQ_MAX: {'type': ['number', 'null'], 'example': 1800.0},
            },
            'required': [],
            'additionalProperties': False,
        }