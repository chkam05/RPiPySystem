from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from core.system.enums.disk_type import DiskType


@dataclass
class DiskUsage(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_DEV_NAME: ClassVar[str] = 'dev_name'
    FIELD_LABEL: ClassVar[str] = 'label'
    FIELD_UUID: ClassVar[str] = 'uuid'
    FIELD_FS_TYPE: ClassVar[str] = 'fs_type'
    FIELD_SIZE_MB: ClassVar[str] = 'size_mb'
    FIELD_FREE_MB: ClassVar[str] = 'free_mb'
    FIELD_USED_MB: ClassVar[str] = 'used_mb'
    FIELD_MOUNT_POINT: ClassVar[str] = 'mount_point'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    dev_name: str
    label: Optional[str] = None
    uuid: Optional[str] = None
    fs_type: DiskType = DiskType.OTHER
    size_mb: Optional[int] = None
    free_mb: Optional[int] = None
    used_mb: Optional[int] = None
    mount_point: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> DiskUsage:
        return cls(
            dev_name=d[cls.FIELD_DEV_NAME],
            label=d.get(cls.FIELD_LABEL),
            uuid=d.get(cls.FIELD_UUID),
            fs_type=DiskType.from_str(d.get(cls.FIELD_FS_TYPE, DiskType.OTHER.value)),
            size_mb=d.get(cls.FIELD_SIZE_MB),
            free_mb=d.get(cls.FIELD_FREE_MB),
            used_mb=d.get(cls.FIELD_USED_MB),
            mount_point=d.get(cls.FIELD_MOUNT_POINT),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_DEV_NAME: self.dev_name,
            self.FIELD_LABEL: self.label,
            self.FIELD_UUID: self.uuid,
            self.FIELD_FS_TYPE: self.fs_type.value,
            self.FIELD_SIZE_MB: self.size_mb,
            self.FIELD_FREE_MB: self.free_mb,
            self.FIELD_USED_MB: self.used_mb,
            self.FIELD_MOUNT_POINT: self.mount_point,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_DEV_NAME: {'type': 'string', 'example': 'mmcblk0p1', 'description': 'Device or partition name.'},
                cls.FIELD_LABEL: {'type': 'string', 'nullable': True, 'example': 'bootfs', 'description': 'Filesystem label.'},
                cls.FIELD_UUID: {'type': 'string', 'nullable': True, 'example': '37d2cb52-0000-0000-0000-000000000000', 'description': 'Filesystem UUID.'},
                cls.FIELD_FS_TYPE: {'type': 'string', 'enum': DiskType.get_all_str(), 'example': DiskType.EXT4.value, 'description': 'Filesystem type.'},
                cls.FIELD_SIZE_MB: {'type': 'integer', 'nullable': True, 'example': 32768, 'description': 'Total partition size in MB.'},
                cls.FIELD_FREE_MB: {'type': 'integer', 'nullable': True, 'example': 12000, 'description': 'Free partition space in MB.'},
                cls.FIELD_USED_MB: {'type': 'integer', 'nullable': True, 'example': 20768, 'description': 'Used partition space in MB.'},
                cls.FIELD_MOUNT_POINT: {'type': 'string', 'nullable': True, 'example': '/', 'description': 'Mount point path.'},
            },
            'required': [cls.FIELD_DEV_NAME, cls.FIELD_FS_TYPE],
        }
