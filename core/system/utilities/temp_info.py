from __future__ import annotations
from typing import List

from core.system.models.temperature_info import TemperatureInfo
from core.system.utilities._helpers import psutil, read_first_existing


class TempInfoUtility:
    def get_info(self) -> TemperatureInfo:
        temps = self._read_psutil_temperatures()
        if not temps:
            temp = self._read_thermal_zone_temperature()
            temps = [temp] if temp is not None else []

        if not temps:
            return TemperatureInfo()

        return TemperatureInfo(temp_c=temps[0], max_temp_c=max(temps))

    def _read_psutil_temperatures(self) -> List[float]:
        if not psutil or not hasattr(psutil, 'sensors_temperatures'):
            return []

        try:
            sensors = psutil.sensors_temperatures(fahrenheit=False)
        except (AttributeError, OSError):
            return []

        values: List[float] = []
        for entries in sensors.values():
            for entry in entries:
                if entry.current is not None:
                    values.append(float(entry.current))

        return values

    def _read_thermal_zone_temperature(self) -> float | None:
        value = read_first_existing(['/sys/class/thermal/thermal_zone0/temp'])
        if value is None:
            return None

        try:
            raw = float(value)
        except ValueError:
            return None

        return raw / 1000 if raw > 1000 else raw
