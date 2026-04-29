from __future__ import annotations
import os

from core.system.enums.disk_type import DiskType
from core.system.models.disk_usage import DiskUsage
from core.system.utilities._helpers import bytes_to_mb, psutil, run_command


class DiskInfoUtility:
    def get_disks(self, include_pseudo: bool = False) -> list[DiskUsage]:
        disks = self._get_partitions(include_pseudo=include_pseudo)
        disks.extend(self._get_swap_partitions())
        return disks

    def _get_partitions(self, include_pseudo: bool = False) -> list[DiskUsage]:
        if not psutil:
            return []

        result: list[DiskUsage] = []
        for partition in psutil.disk_partitions(all=include_pseudo):
            usage = None
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except OSError:
                pass

            result.append(DiskUsage(
                dev_name=os.path.basename(partition.device) or partition.device,
                label=self._find_lsblk_value(partition.device, 'LABEL'),
                uuid=self._find_lsblk_value(partition.device, 'UUID'),
                fs_type=self._disk_type(partition.fstype),
                size_mb=bytes_to_mb(usage.total) if usage else None,
                free_mb=bytes_to_mb(usage.free) if usage else None,
                used_mb=bytes_to_mb(usage.used) if usage else None,
                mount_point=partition.mountpoint,
            ))

        return result

    def _get_swap_partitions(self) -> list[DiskUsage]:
        output = run_command(['swapon', '--show=NAME,SIZE,USED', '--bytes', '--noheadings'])
        if not output:
            return []

        result: list[DiskUsage] = []
        for line in output.splitlines():
            parts = line.split()
            if not parts:
                continue
            size = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
            used = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
            result.append(DiskUsage(
                dev_name=os.path.basename(parts[0]) or parts[0],
                fs_type=DiskType.SWAP,
                size_mb=bytes_to_mb(size),
                used_mb=bytes_to_mb(used),
                free_mb=bytes_to_mb(size - used) if size is not None and used is not None else None,
                mount_point='[SWAP]',
            ))

        return result

    def _find_lsblk_value(self, device: str, column: str) -> str | None:
        output = run_command(['lsblk', '-no', column, device])
        return output.splitlines()[0].strip() if output else None

    def _disk_type(self, value: str | None) -> DiskType:
        if not value:
            return DiskType.OTHER
        try:
            return DiskType.from_str(value)
        except ValueError:
            return DiskType.OTHER
