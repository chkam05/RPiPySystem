from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List

from core.data.public_data_model import PublicDataModel
from core.system.models.cpu_info import CPUInfo
from core.system.models.cpu_usage import CPUUsage
from core.system.models.disk_usage import DiskUsage
from core.system.models.mem_usage import MemUsage
from core.system.models.temperature_info import TemperatureInfo


@dataclass
class OSUsage(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_CPU: ClassVar[str] = 'cpu'
    FIELD_CPU_USAGE: ClassVar[str] = 'cpu_usage'
    FIELD_TEMPERATURE: ClassVar[str] = 'temperature'
    FIELD_MEMORY: ClassVar[str] = 'memory'
    FIELD_DISKS: ClassVar[str] = 'disks'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    cpu: CPUInfo = field(default_factory=CPUInfo)
    cpu_usage: CPUUsage = field(default_factory=CPUUsage)
    temperature: TemperatureInfo = field(default_factory=TemperatureInfo)
    memory: MemUsage = field(default_factory=MemUsage)
    disks: List[DiskUsage] = field(default_factory=list)

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> OSUsage:
        return cls(
            cpu=CPUInfo.from_dict(d.get(cls.FIELD_CPU, {})),
            cpu_usage=CPUUsage.from_dict(d.get(cls.FIELD_CPU_USAGE, {})),
            temperature=TemperatureInfo.from_dict(d.get(cls.FIELD_TEMPERATURE, {})),
            memory=MemUsage.from_dict(d.get(cls.FIELD_MEMORY, {})),
            disks=DiskUsage.from_dict_list(d.get(cls.FIELD_DISKS, [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_CPU: self.cpu.to_dict(),
            self.FIELD_CPU_USAGE: self.cpu_usage.to_dict(),
            self.FIELD_TEMPERATURE: self.temperature.to_dict(),
            self.FIELD_MEMORY: self.memory.to_dict(),
            self.FIELD_DISKS: DiskUsage.to_dict_list(self.disks),
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_CPU: {
                    **CPUInfo.schema_public(),
                    'example': CPUInfo(model='ARM Cortex-A72', architecture='aarch64', cores_logical=4).to_dict(),
                    'description': 'CPU hardware information.',
                },
                cls.FIELD_CPU_USAGE: {
                    **CPUUsage.schema_public(),
                    'example': CPUUsage(cores={'cpu0': 3.4, 'cpu1': 7.9}, total=5.2).to_dict(),
                    'description': 'Current CPU usage.',
                },
                cls.FIELD_TEMPERATURE: {
                    **TemperatureInfo.schema_public(),
                    'example': TemperatureInfo(temp_c=42.5, max_temp_c=48.2).to_dict(),
                    'description': 'Current temperature information.',
                },
                cls.FIELD_MEMORY: {
                    **MemUsage.schema_public(),
                    'example': MemUsage(total=3796, free=168, used=2437, available=1211).to_dict(),
                    'description': 'Current memory usage.',
                },
                cls.FIELD_DISKS: {
                    **DiskUsage.schema_public_list(),
                    'example': [DiskUsage(dev_name='mmcblk0p1', mount_point='/').to_dict()],
                    'description': 'Disk and swap usage list.',
                },
            },
            'required': [],
        }
