from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar

from .cpu_info import CPUInfo
from .cpu_usage import CPUUsage
from .disk_usage import DiskUsage
from .mem_usage import MemUsage
from .temperature_info import TemperatureInfo
from utils.models.public_model import PublicModel


T = TypeVar('T', bound='OSUsage')


@dataclass
class OSUsage(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_CPU: ClassVar[str] = 'cpu'
    FIELD_CPU_USAGE: ClassVar[str] = 'cpu_usage'
    FIELD_TEMPERATURE: ClassVar[str] = 'temperature'
    FIELD_MEMORY: ClassVar[str] = 'memory'
    FIELD_DISKS: ClassVar[str] = 'disks'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    cpu: CPUInfo
    cpu_usage: CPUUsage
    temperature: TemperatureInfo
    memory: MemUsage
    disks: List[DiskUsage]

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> OSUsage:
        return cls(
            cpu=CPUInfo.from_dict(d.get(cls.FIELD_CPU, {})),
            cpu_usage=CPUUsage.from_dict(d.get(cls.FIELD_CPU_USAGE, {})),
            temperature=TemperatureInfo.from_dict(d.get(cls.FIELD_TEMPERATURE, {})),
            memory=MemUsage.from_dict(d.get(cls.FIELD_MEMORY, {})),
            disks=DiskUsage.list_from_dicts(d.get(cls.FIELD_DISKS, []))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_CPU: self.cpu.to_dict(),
            self.FIELD_CPU_USAGE: self.cpu_usage.to_dict(),
            self.FIELD_TEMPERATURE: self.temperature.to_dict(),
            self.FIELD_MEMORY: self.memory.to_dict(),
            self.FIELD_DISKS: DiskUsage.list_to_dicts(self.disks),
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CPU: CPUInfo.schema_public(),
                cls.FIELD_CPU_USAGE: CPUUsage.schema_public(),
                cls.FIELD_TEMPERATURE: TemperatureInfo.schema_public(),
                cls.FIELD_MEMORY: MemUsage.schema_public(),
                cls.FIELD_DISKS: DiskUsage.schema_public_list(),
            },
            'required': [
                cls.FIELD_CPU,
                cls.FIELD_CPU_USAGE,
                cls.FIELD_TEMPERATURE,
                cls.FIELD_MEMORY,
                cls.FIELD_DISKS
            ],
            'additionalProperties': False,
        }