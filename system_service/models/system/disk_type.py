from utils.base_str_enum import BaseStrEnum


class DiskType(BaseStrEnum):
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