from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

from system_service.models.system.disk_usage import DiskUsage
from system_service.models.system.mem_usage import MemUsage
from system_service.models.system.os_temp_info import OSTempInfo
from system_service.models.system.cpu_info import CPUInfo
from system_service.models.system.cpu_usage import CPUUsage


@dataclass
class OSUsage:
    # --- Field-name constants ---
    FIELD_CPU: ClassVar[str] = 'cpu'
    FIELD_CPU_USAGE: ClassVar[str] = 'cpu_usage'
    FIELD_TEMPERATURE: ClassVar[str] = 'temperature'
    FIELD_MEMORY: ClassVar[str] = 'memory'
    FIELD_DISKS: ClassVar[str] = 'disks'

    # --- Fields ---
    cpu: CPUInfo
    cpu_usage: CPUUsage
    temperature: OSTempInfo
    memory: MemUsage
    disks: List[DiskUsage]

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'OSUsage':
        return cls(
            cpu=CPUInfo.from_dict(d.get(cls.FIELD_CPU, {})),
            cpu_usage=CPUUsage.from_dict(d.get(cls.FIELD_CPU_USAGE, {})),
            temperature=OSTempInfo.from_dict(d.get(cls.FIELD_TEMPERATURE, {})),
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

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CPU: CPUInfo.schema_public(),
                cls.FIELD_CPU_USAGE: CPUUsage.schema_public(),
                cls.FIELD_TEMPERATURE: OSTempInfo.schema_public(),
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