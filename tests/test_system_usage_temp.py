import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.usage.temperature_info import TemperatureInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemTempUsage(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_temperature_info(self) -> TemperatureInfo:
        # Make request
        resp = self.client.get('/usage/temperature', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, dict)

        # Model mapping
        temp = TemperatureInfo.from_dict(data)
        self.is_instance_of_type(temp, TemperatureInfo, f'Response is not an instance of TemperatureInfo.')

        return temp
    
    def _read_system_temperature_c(self) -> float | None:
        """
        Attempting to read CPU temperature from different thermal_zones.
        Returns the temperature in °C as float or None if not possible.
        """
        # Most common case on Linux/RPi: /sys/class/thermal/thermal_zone*/temp.
        candidates = sorted(glob.glob('/sys/class/thermal/thermal_zone*/temp'))

        for path in candidates:
            try:
                with open(path, 'r') as f:
                    raw = f.read().strip()
                if not raw:
                    continue

                value = int(raw)
                # Most systems report in millicels.
                if value > 1000:
                    temp_c = value / 1000.0
                else:
                    temp_c = float(value)

                # Sanity check - if the scope makes sense.
                if -40.0 <= temp_c <= 200.0:
                    return temp_c
            except Exception:
                continue

        return None

    @testcase
    def test_01_temperature_basic_shape(self) -> None:
        info = self._get_temperature_info()
        
        # temp_c – if present, the real temperature (Celsius).
        if info.temp_c is not None:
            self.is_instance_of_type(info.temp_c, (int, float))
            # Typical range for CPU: -40 .. 120 °C (leave a large margin).
            self.is_true(
                -40.0 <= float(info.temp_c) <= 120.0,
                f'temp_c out of expected range: {info.temp_c}'
            )

        # max_temp_c – if present, then > temp_c and within a reasonable range.
        if info.max_temp_c is not None:
            self.is_instance_of_type(info.max_temp_c, (int, float))
            self.is_true(
                40.0 <= float(info.max_temp_c) <= 130.0,
                f'max_temp_c out of expected range: {info.max_temp_c}'
            )

            if info.temp_c is not None:
                self.is_true(
                    info.max_temp_c >= info.temp_c,
                    f'max_temp_c ({info.max_temp_c}) < temp_c ({info.temp_c})'
                )
    
    @testcase
    def test_02_temperature_matches_system(self) -> None:
        """
        Compares temp_c from API with the temperature read from /sys/class/thermal.
        If the system does not provide such information, the test ends without
        additional assertions (best effort).
        """
        info = self._get_temperature_info()

        # If the API doesn't return temp_c at all, there's nothing to compare it to.
        if info.temp_c is None:
            return

        sys_temp = self._read_system_temperature_c()
        if sys_temp is None:
            # No system data - do not make further assertions.
            return

        # The API temperature should be close to the system temperature (with a margin).
        # Start e.g. 15°C tolerance for different sensors / rounding / delays.
        diff = abs(float(info.temp_c) - sys_temp)
        self.is_true(
            diff <= 15.0,
            f'API temperature ({info.temp_c}°C) differs too much from system temperature '
            f'({sys_temp}°C), diff={diff}°C'
        )


if __name__ == '__main__':
    TestSystemTempUsage().run()