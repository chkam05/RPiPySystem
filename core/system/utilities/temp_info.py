from __future__ import annotations
from typing import List

from core.system.models.temperature_info import TemperatureInfo
from core.system.utilities._helpers import psutil, read_first_existing


class TempInfoUtility:
    def get_info(self) -> TemperatureInfo:
        temps = self._read_psutil_temperatures()
        max_temp = self._read_psutil_critical_temperature()
        if not temps:
            temp = self._read_thermal_zone_temperature()
            temps = [temp] if temp is not None else []
        if max_temp is None:
            max_temp = self._read_thermal_zone_critical_temperature()

        if not temps:
            return TemperatureInfo(max_temp_c=max_temp)

        return TemperatureInfo(temp_c=temps[0], max_temp_c=max_temp)

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

    def _read_psutil_critical_temperature(self) -> float | None:
        if not psutil or not hasattr(psutil, 'sensors_temperatures'):
            return None

        try:
            sensors = psutil.sensors_temperatures(fahrenheit=False)
        except (AttributeError, OSError):
            return None

        values: List[float] = []
        for entries in sensors.values():
            for entry in entries:
                critical = getattr(entry, 'critical', None)
                high = getattr(entry, 'high', None)
                if critical is not None:
                    values.append(float(critical))
                elif high is not None:
                    values.append(float(high))

        return min(values) if values else None

    def _read_thermal_zone_temperature(self) -> float | None:
        value = read_first_existing(['/sys/class/thermal/thermal_zone0/temp'])
        if value is None:
            return None

        try:
            raw = float(value)
        except ValueError:
            return None

        return raw / 1000 if raw > 1000 else raw

    def _read_thermal_zone_critical_temperature(self) -> float | None:
        values: List[float] = []
        for zone_index in range(0, 32):
            zone_path = f'/sys/class/thermal/thermal_zone{zone_index}'
            for trip_index in range(0, 16):
                type_value = read_first_existing([f'{zone_path}/trip_point_{trip_index}_type'])
                temp_value = read_first_existing([f'{zone_path}/trip_point_{trip_index}_temp'])
                if type_value is None or temp_value is None:
                    continue
                if type_value.strip().casefold() not in {'critical', 'hot'}:
                    continue
                try:
                    raw = float(temp_value)
                except ValueError:
                    continue
                values.append(raw / 1000 if raw > 1000 else raw)

        return min(values) if values else None
