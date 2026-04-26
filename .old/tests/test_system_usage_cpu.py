import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.usage.cpu_usage import CPUUsage
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemUsageCPU(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_cpu_usage(self) -> CPUUsage:
        # Make request
        resp = self.client.get('/usage/cpu?cpu_sample_time=3', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, dict)

        # Model mapping
        usage = CPUUsage.from_dict(data)
        self.is_instance_of_type(usage, CPUUsage, f'Response is not an instance of CPUUsage.')

        return usage

    @testcase
    def test_01_cpuusage_basic_shape(self) -> None:
        usage = self._get_cpu_usage()

        self.is_instance_of_type(usage.cores, dict)
        self.is_not_empty(usage.cores)

        cpu_name_pattern = re.compile(r'^cpu\d+$')

        for name, value in usage.cores.items():
            # Core name e.g. cpu0, cpu1, ...
            self.is_instance_of_type(name, str)
            self.is_true(
                bool(cpu_name_pattern.match(name)),
                f'Invalid core name: {name!r}'
            )

            # value: float in the range 0–100 (if already counted).
            self.is_instance_of_type(value, (int, float))
            self.is_true(
                0.0 <= float(value) <= 100.0,
                f'CPU usage for {name} is out of [0, 100]: {value}'
            )
        
        # Total: Optional[float].
        if usage.total is not None:
            self.is_instance_of_type(usage.total, (int, float))
            self.is_true(
                0.0 <= float(usage.total) <= 100.0,
                f'Total CPU usage out of [0, 100]: {usage.total}'
            )

        # The number of cores should match os.cpu_count().
        system_logical = os.cpu_count()
        if system_logical is not None:
            self.are_equal(
                len(usage.cores),
                system_logical,
                f'API cores count ({len(usage.cores)}) != os.cpu_count() ({system_logical})'
            )
    
    @testcase
    def test_02_cpuusage_eventually_non_zero(self) -> None:
        """
        Endpoint sometimes returns 0.0 if sampling is too short/failed.
        This test gives it several attempts, but requires that at least once 
        some value > 0 (total or any of the cores) occurs.
        """
        max_attempts = 5
        got_non_zero = False

        for attempt in range(1, max_attempts + 1):
            usage = self._get_cpu_usage()

            # Sanity: cores always non-empty.
            self.is_instance_of_type(usage.cores, dict)
            self.is_not_empty(usage.cores)

            any_core_non_zero = any(
                isinstance(v, (int, float)) and float(v) > 0.0
                for v in usage.cores.values()
            )

            total_non_zero = (
                isinstance(usage.total, (int, float)) and float(usage.total) > 0.0
            )

            if any_core_non_zero or total_non_zero:
                got_non_zero = True
                break

        self.is_true(
            got_non_zero,
            f'CPU usage remained zero in all {max_attempts} attempts; '
            f'backend may not be sampling usage correctly.'
        )


if __name__ == '__main__':
    TestSystemUsageCPU().run()