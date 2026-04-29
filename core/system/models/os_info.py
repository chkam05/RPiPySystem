from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from core.system.models._conversion import datetime_from_str, datetime_to_str


@dataclass
class OSInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_DISTRIBUTION: ClassVar[str] = 'distribution'
    FIELD_DISTRIBUTION_CODENAME: ClassVar[str] = 'distribution_codename'
    FIELD_DISTRIBUTION_VERSION: ClassVar[str] = 'distribution_version'
    FIELD_KERNEL: ClassVar[str] = 'kernel'
    FIELD_KERNEL_NAME: ClassVar[str] = 'kernel_name'
    FIELD_KERNEL_VERSION: ClassVar[str] = 'kernel_version'
    FIELD_RELEASE_VERSION: ClassVar[str] = 'release_version'
    FIELD_ARCHITECTURE: ClassVar[str] = 'architecture'
    FIELD_COMPILATION_DATE: ClassVar[str] = 'compilation_date'
    FIELD_NETWORK_NAME: ClassVar[str] = 'network_name'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    distribution: Optional[str] = None
    distribution_codename: Optional[str] = None
    distribution_version: Optional[str] = None
    kernel: Optional[str] = None
    kernel_name: Optional[str] = None
    kernel_version: Optional[str] = None
    release_version: Optional[str] = None
    architecture: Optional[str] = None
    compilation_date: Optional[datetime] = None
    network_name: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> OSInfo:
        return cls(
            distribution=d.get(cls.FIELD_DISTRIBUTION),
            distribution_codename=d.get(cls.FIELD_DISTRIBUTION_CODENAME),
            distribution_version=d.get(cls.FIELD_DISTRIBUTION_VERSION),
            kernel=d.get(cls.FIELD_KERNEL),
            kernel_name=d.get(cls.FIELD_KERNEL_NAME),
            kernel_version=d.get(cls.FIELD_KERNEL_VERSION),
            release_version=d.get(cls.FIELD_RELEASE_VERSION),
            architecture=d.get(cls.FIELD_ARCHITECTURE),
            compilation_date=datetime_from_str(d.get(cls.FIELD_COMPILATION_DATE)),
            network_name=d.get(cls.FIELD_NETWORK_NAME),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_DISTRIBUTION: self.distribution,
            self.FIELD_DISTRIBUTION_CODENAME: self.distribution_codename,
            self.FIELD_DISTRIBUTION_VERSION: self.distribution_version,
            self.FIELD_KERNEL: self.kernel,
            self.FIELD_KERNEL_NAME: self.kernel_name,
            self.FIELD_KERNEL_VERSION: self.kernel_version,
            self.FIELD_RELEASE_VERSION: self.release_version,
            self.FIELD_ARCHITECTURE: self.architecture,
            self.FIELD_COMPILATION_DATE: datetime_to_str(self.compilation_date),
            self.FIELD_NETWORK_NAME: self.network_name,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_DISTRIBUTION: {'type': 'string', 'nullable': True, 'example': 'Debian GNU/Linux 13 (trixie)', 'description': 'Operating system distribution name.'},
                cls.FIELD_DISTRIBUTION_CODENAME: {'type': 'string', 'nullable': True, 'example': 'trixie', 'description': 'Distribution codename.'},
                cls.FIELD_DISTRIBUTION_VERSION: {'type': 'string', 'nullable': True, 'example': '13', 'description': 'Distribution version.'},
                cls.FIELD_KERNEL: {'type': 'string', 'nullable': True, 'example': 'Linux', 'description': 'Kernel family name.'},
                cls.FIELD_KERNEL_NAME: {'type': 'string', 'nullable': True, 'example': 'debian', 'description': 'Kernel or distribution identifier.'},
                cls.FIELD_KERNEL_VERSION: {'type': 'string', 'nullable': True, 'example': '#1 SMP PREEMPT Debian 1:6.12.47-1+rpt1', 'description': 'Kernel build version string.'},
                cls.FIELD_RELEASE_VERSION: {'type': 'string', 'nullable': True, 'example': '6.12.47+rpt-rpi-v8', 'description': 'Kernel release version.'},
                cls.FIELD_ARCHITECTURE: {'type': 'string', 'nullable': True, 'example': 'aarch64', 'description': 'Machine architecture.'},
                cls.FIELD_COMPILATION_DATE: {'type': 'string', 'nullable': True, 'example': '2026-04-29T12:00:00', 'description': 'Kernel compilation date if detected.'},
                cls.FIELD_NETWORK_NAME: {'type': 'string', 'nullable': True, 'example': 'raspberrypi', 'description': 'System hostname.'},
            },
            'required': [],
        }
