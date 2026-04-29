from __future__ import annotations

from core.system.models.mem_usage import MemUsage
from core.system.utilities._helpers import bytes_to_mb, psutil


class MemInfoUtility:
    def get_usage(self) -> MemUsage:
        if not psutil:
            return self._get_usage_from_proc()

        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        total = bytes_to_mb(vm.total)
        free = bytes_to_mb(vm.free)
        used = bytes_to_mb(vm.used)
        available = bytes_to_mb(vm.available)
        swap_total = bytes_to_mb(swap.total)
        swap_free = bytes_to_mb(swap.free)
        swap_used = bytes_to_mb(swap.used)

        return MemUsage(
            total=total,
            free=free,
            used=used,
            available=available,
            buff_cache=bytes_to_mb(getattr(vm, 'buffers', 0) + getattr(vm, 'cached', 0)),
            shared=bytes_to_mb(getattr(vm, 'shared', 0)),
            swap_total=swap_total,
            swap_free=swap_free,
            swap_used=swap_used,
            sum_total=(total or 0) + (swap_total or 0),
            sum_free=(free or 0) + (swap_free or 0),
            sum_used=(used or 0) + (swap_used or 0),
        )

    def _get_usage_from_proc(self) -> MemUsage:
        values: dict[str, int] = {}
        try:
            with open('/proc/meminfo', 'r', encoding='utf-8') as f:
                for line in f:
                    key, raw_value = line.split(':', 1)
                    parts = raw_value.strip().split()
                    if parts and parts[0].isdigit():
                        values[key] = int(parts[0]) // 1024
        except (OSError, ValueError):
            return MemUsage()

        total = values.get('MemTotal')
        free = values.get('MemFree')
        available = values.get('MemAvailable')
        buff_cache = values.get('Buffers', 0) + values.get('Cached', 0) + values.get('SReclaimable', 0)
        used = total - free - buff_cache if total is not None and free is not None else None
        swap_total = values.get('SwapTotal')
        swap_free = values.get('SwapFree')
        swap_used = swap_total - swap_free if swap_total is not None and swap_free is not None else None

        return MemUsage(
            total=total,
            free=free,
            used=used,
            available=available,
            buff_cache=buff_cache,
            shared=values.get('Shmem'),
            swap_total=swap_total,
            swap_free=swap_free,
            swap_used=swap_used,
            sum_total=(total or 0) + (swap_total or 0),
            sum_free=(free or 0) + (swap_free or 0),
            sum_used=(used or 0) + (swap_used or 0),
        )
