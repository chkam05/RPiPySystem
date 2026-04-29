from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class CPUUsage(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_CORES: ClassVar[str] = 'cores'
    FIELD_TOTAL: ClassVar[str] = 'total'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    cores: Dict[str, float] = field(default_factory=dict)
    total: Optional[float] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CPUUsage:
        return cls(cores=d.get(cls.FIELD_CORES, {}), total=d.get(cls.FIELD_TOTAL))

    def to_dict(self) -> Dict[str, Any]:
        return {self.FIELD_CORES: self.cores, self.FIELD_TOTAL: self.total}

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CORES: {
                    'type': 'object',
                    'additionalProperties': {'type': 'number'},
                    'example': {'cpu0': 3.4, 'cpu1': 7.9},
                    'description': 'CPU usage per logical core in percent.',
                },
                cls.FIELD_TOTAL: {'type': 'number', 'nullable': True, 'example': 5.2, 'description': 'Total CPU usage in percent.'},
            },
            'required': [cls.FIELD_CORES],
        }
