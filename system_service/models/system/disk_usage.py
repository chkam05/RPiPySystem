from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

from system_service.models.system.disk_type import DiskType


@dataclass
class DiskUsage:
    # --- Field-name constants ---
    FIELD_DEV_NAME: ClassVar[str] = 'dev_name'
    FIELD_LABEL: ClassVar[str] = 'label'
    FIELD_UUID: ClassVar[str] = 'uuid'
    FIELD_FS_TYPE: ClassVar[str] = 'fs_type'
    FIELD_SIZE_MB: ClassVar[str] = 'size_mb'
    FIELD_FREE_MB: ClassVar[str] = 'free_mb'
    FIELD_USED_MB: ClassVar[str] = 'used_mb'
    FIELD_MOUNT_POINT: ClassVar[str] = 'mount_point'

    # --- Fields ---
    dev_name: str               # e.g.: 'mmcblk0p1'.
    label: Optional[str]        # e.g.: 'bootfs'.
    uuid: Optional[str]         # e.g.: '37d2cb52-...'.
    fs_type: DiskType           # e.g.: DiskType.VFAT.
    size_mb: Optional[int]
    free_mb: Optional[int]
    used_mb: Optional[int]
    mount_point: Optional[str]  # e.g.: '/', '/boot', '[SWAP]'

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'DiskUsage':
        fs_str = d.get(cls.FIELD_FS_TYPE)
        fs_val: DiskType.OTHER
        if fs_str:
            try:
                fs_val = DiskType(fs) if isinstance(fs, str) else DiskType.OTHER
            except (TypeError, ValueError):
                fs_val = DiskType.OTHER
        
        return cls(
            dev_name=d.get(cls.FIELD_DEV_NAME),
            label=d.get(cls.FIELD_LABEL),
            uuid=d.get(cls.FIELD_UUID),
            fs_type=fs_val,
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
            self.FIELD_FS_TYPE: str(self.fs_type),
            self.FIELD_SIZE_MB: self.size_mb,
            self.FIELD_FREE_MB: self.free_mb,
            self.FIELD_USED_MB: self.used_mb,
            self.FIELD_MOUNT_POINT: self.mount_point,
        }

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, rows: List[Dict[str, Any]]) -> List['DiskUsage']:
        return [cls.from_dict(r) for r in (rows or [])]

    @staticmethod
    def list_to_dicts(items: List['DiskUsage']) -> List[Dict[str, Any]]:
        return [i.to_public() for i in (items or [])]

    @classmethod
    def list_to_public(cls, items: List['DiskUsage']) -> List[Dict[str, Any]]:
        return cls.list_to_dicts(items)

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        disk_type_values = DiskType.get_all_str()
        
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_DEV_NAME: {'type': 'string', 'example': 'mmcblk0p1'},
                cls.FIELD_LABEL: {'type': ['string', 'null'], 'example': 'bootfs'},
                cls.FIELD_UUID: {'type': ['string', 'null'], 'example': '37d2cb52-513e-40e1-b90f-213aa6096cba'},
                cls.FIELD_FS_TYPE: {'type': 'string', 'enum': disk_type_values, 'example': 'vfat'},
                cls.FIELD_SIZE_MB: {'type': ['integer', 'null'], 'example': 256},
                cls.FIELD_FREE_MB: {'type': ['integer', 'null'], 'example': 136},
                cls.FIELD_USED_MB: {'type': ['integer', 'null'], 'example': 120},
                cls.FIELD_MOUNT_POINT: {'type': ['string', 'null'], 'example': '/boot'},
            },
            'required': [cls.FIELD_DEV_NAME, cls.FIELD_FS_TYPE],
            'additionalProperties': False,
        }
    
    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }