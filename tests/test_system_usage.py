import re
import sys
from pathlib import Path

from system_service.models.system.usage.disk_usage import DiskUsage
from system_service.models.system.usage.mem_usage import MemUsage
from system_service.models.system.usage.temperature_info import TemperatureInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.usage.cpu_usage import CPUUsage
from system_service.models.system.usage.os_usage import OSUsage
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemUsage(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_usage(self) -> OSUsage:
        # Make request
        resp = self.client.get('/usage/', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, dict)

        # Model mapping
        usage = OSUsage.from_dict(data)
        self.is_instance_of_type(usage, OSUsage, f'Response is not an instance of OSUsage.')

        return usage

    @testcase
    def test_01_osusage_basic_shape(self) -> None:
        usage = self._get_usage()
        
        # A few sanity checks.
        if usage.cpu.cores_logical is not None:
            self.is_true(usage.cpu.cores_logical > 0, 'cores_logical must be > 0')

        if usage.cpu.cores_physical is not None:
            self.is_true(usage.cpu.cores_physical > 0, 'cores_physical must be > 0')

        # --- CPU usage ---
        self.is_instance_of_type(usage.cpu_usage, CPUUsage)
        self.is_instance_of_type(usage.cpu_usage.cores, dict)
        self.is_not_empty(usage.cpu_usage.cores)

        cpu_name_pattern = re.compile(r'^cpu\d+$')

        for name, value in usage.cpu_usage.cores.items():
            self.is_true(
                bool(cpu_name_pattern.match(name)),
                f'Invalid core name in OSUsage.cpu_usage.cores: {name!r}'
            )
            self.is_true(0.0 <= float(value) <= 100.0)

        if usage.cpu_usage.total is not None:
            self.is_true(0.0 <= float(usage.cpu_usage.total) <= 100.0)

        # --- Temperature ---
        self.is_instance_of_type(usage.temperature, TemperatureInfo)
        if usage.temperature.temp_c is not None:
            self.is_true(-40.0 <= float(usage.temperature.temp_c) <= 120.0)

        # --- Memory ---
        self.is_instance_of_type(usage.memory, MemUsage)
        if usage.memory.total is not None:
            self.is_true(usage.memory.total >= 0)

        # --- Disks ---
        self.is_instance_of_type(usage.disks, list)
        self.is_not_empty(usage.disks)
        for d in usage.disks:
            self.is_instance_of_type(d, DiskUsage)
            self.is_instance_of_type(d.dev_name, str)
            self.is_not_empty(d.dev_name)


if __name__ == '__main__':
    TestSystemUsage().run()