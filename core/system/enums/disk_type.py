from __future__ import annotations
from core.data.enum_str import StrEnum


class DiskType(StrEnum):
    BTRFS = 'btrfs'
    EXFAT = 'exfat'
    EXT2 = 'ext2'
    EXT3 = 'ext3'
    EXT4 = 'ext4'
    NTFS = 'ntfs'
    OTHER = 'other'
    SWAP = 'swap'
    VFAT = 'vfat'
    XFS = 'xfs'
