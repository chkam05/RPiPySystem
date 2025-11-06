from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional


@dataclass
class OSInfo:
    # --- Field-name constants ---
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

    DATETIME_FORMAT: ClassVar[str] = '%Y-%m-%d'

    # --- Fields ---
    distribution: Optional[str]             # Debian GNU/Linux
    distribution_codename: Optional[str]    # trixie
    distribution_version: Optional[str]     # 13.1
    kernel: Optional[str]                   # Linux
    kernel_name: Optional[str]              # GNU/Linux
    kernel_version: Optional[str]           # 1:6.12.47-1+rpt1
    release_version: Optional[str]          # 6.12.47+rpt-rpi-v8
    architecture: Optional[str]             # aarch64
    compilation_date: Optional[datetime]
    network_name: Optional[str]             # raspberrypi
    
    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'OSInfo':
        date_str = d.get(cls.FIELD_COMPILATION_DATE)
        date_val: Optional[datetime] = None
        if date_str:
            try:
                date_val = datetime.strptime(date_str, cls.DATETIME_FORMAT)
            except (TypeError, ValueError):
                date_val = None
        
        return cls(
            distribution=d.get(cls.FIELD_DISTRIBUTION),
            distribution_codename=d.get(cls.FIELD_DISTRIBUTION_CODENAME),
            distribution_version=d.get(cls.FIELD_DISTRIBUTION_VERSION),
            kernel=d.get(cls.FIELD_KERNEL),
            kernel_name=d.get(cls.FIELD_KERNEL_NAME),
            kernel_version=d.get(cls.FIELD_KERNEL_VERSION),
            release_version=d.get(cls.FIELD_RELEASE_VERSION),
            architecture=d.get(cls.FIELD_ARCHITECTURE),
            compilation_date=date_val,
            network_name=d.get(cls.FIELD_NETWORK_NAME)
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
            self.FIELD_COMPILATION_DATE: (
                self.compilation_date.strftime(self.DATETIME_FORMAT)
                if self.compilation_date else None
            ),
            self.FIELD_NETWORK_NAME: self.network_name
        }
    
    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_DISTRIBUTION: {'type': ['string', 'null'], 'example': 'Debian GNU/Linux'},
                cls.FIELD_DISTRIBUTION_CODENAME: {'type': ['string', 'null'], 'example': 'trixie'},
                cls.FIELD_DISTRIBUTION_VERSION: {'type': ['string', 'null'], 'example': '13.1'},
                cls.FIELD_KERNEL: {'type': ['string', 'null'], 'example': 'Linux'},
                cls.FIELD_KERNEL_NAME: {'type': ['string', 'null'], 'example': 'GNU/Linux'},
                cls.FIELD_KERNEL_VERSION: {'type': ['string', 'null'], 'example': '1:6.12.47-1+rpt1'},
                cls.FIELD_RELEASE_VERSION: {'type': ['string', 'null'], 'example': '6.12.47+rpt-rpi-v8'},
                cls.FIELD_ARCHITECTURE: {'type': ['string', 'null'], 'example': 'aarch64'},
                cls.FIELD_COMPILATION_DATE: {'type': ['string', 'null'], 'format': 'date-time', 'example': '2025-09-16'},
                cls.FIELD_NETWORK_NAME: {'type': ['string', 'null'], 'example': 'raspberrypi'}
            },
            'required': [],
            'additionalProperties': False
        }