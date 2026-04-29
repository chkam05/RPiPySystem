from __future__ import annotations
from typing import Optional
import platform
import os

from core.system.models.cpu_info import CPUInfo
from core.system.models.cpu_usage import CPUUsage
from core.system.utilities._helpers import psutil, read_first_existing


class CPUInfoUtility:
    def get_info(self) -> CPUInfo:
        freq = psutil.cpu_freq() if psutil else None
        return CPUInfo(
            model=self._get_model(),
            architecture=platform.machine() or None,
            cores_logical=psutil.cpu_count(logical=True) if psutil else os.cpu_count(),
            cores_physical=psutil.cpu_count(logical=False) if psutil else None,
            freq=freq.current if freq else self._read_current_freq(),
            freq_min=freq.min if freq else None,
            freq_max=freq.max if freq else None,
        )

    def get_usage(self, interval: float = 0.1) -> CPUUsage:
        if not psutil:
            return CPUUsage()

        per_cpu = psutil.cpu_percent(interval=interval, percpu=True)
        total = psutil.cpu_percent(interval=None, percpu=False)
        return CPUUsage(cores={f'cpu{i}': value for i, value in enumerate(per_cpu)}, total=total)

    def _get_model(self) -> Optional[str]:
        values: dict[str, str] = {}
        try:
            with open('/proc/cpuinfo', 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' not in line:
                        continue
                    key, value = line.split(':', 1)
                    values[key.strip().casefold()] = value.strip()
        except OSError:
            pass

        for key in ('model name', 'model', 'hardware'):
            if values.get(key):
                return values[key]

        processor = platform.processor()
        return processor or None

    def _read_current_freq(self) -> Optional[float]:
        value = read_first_existing(['/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'])
        if value is None:
            return None

        try:
            return float(value) / 1000
        except ValueError:
            return None
