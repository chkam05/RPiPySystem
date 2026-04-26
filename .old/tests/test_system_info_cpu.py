from datetime import datetime
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.usage.cpu_info import CPUInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM

class TestSystemInfoCpu(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_cpu_info(self) -> CPUInfo:
        # Make request
        resp = self.client.get('/info/cpu', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_instance_of_type(data, dict)
        self.is_not_empty(data)

        # Model mapping
        cpu = CPUInfo.from_dict(data)
        self.is_instance_of_type(cpu, CPUInfo, f'Response is not an instance of CPUInfo.')

        return cpu

    def _read_cpu_freq_from_proc(self) -> float | None:
        """Read CPU frequency from /sys or /proc. Returns MHz as float."""
        # Most reliable source:
        paths = [
            "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq",
            "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq",
        ]

        for p in paths:
            try:
                if os.path.exists(p):
                    with open(p, "r") as f:
                        khz = int(f.read().strip())
                        return khz / 1000.0
            except Exception:
                pass

        # Fallback via /proc/cpuinfo:
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    line = line.strip().lower()
                    if line.startswith("cpu mhz"):
                        _, val = line.split(":", 1)
                        return float(val.strip())
        except Exception:
            pass

        # If the frequency reading failed, return None.
        return None

    @testcase
    def test_01_cpuinfo_basic_shape(self) -> None:
        cpu = self._get_cpu_info()

        if cpu.architecture is not None:
            self.is_instance_of_type(cpu.architecture, str)
            self.is_not_empty(cpu.architecture)
        
        if cpu.model is not None:
            self.is_instance_of_type(cpu.model, str)
            self.is_not_empty(cpu.model)
        
        for f in (cpu.freq, cpu.freq_min, cpu.freq_max):
            if f is not None:
                self.is_true(f >= 0, "CPU frequency cannot be negative")
        
        if cpu.cores_logical is not None:
            self.is_instance_of_type(cpu.cores_logical, int)
            self.is_true(cpu.cores_logical > 0)
        
        if cpu.cores_physical is not None:
            self.is_instance_of_type(cpu.cores_physical, int)
            self.is_true(cpu.cores_physical > 0)
    
    @testcase
    def test_02_cpuinfo_matches_system(self) -> None:
        cpu = self._get_cpu_info()

        system_arch = platform.machine()
        if cpu.architecture is not None:
            self.are_equal(
                cpu.architecture,
                system_arch,
                f'API architecture does not match system architecture ({system_arch})'
            )

        system_logical = os.cpu_count()
        if cpu.cores_logical is not None and system_logical is not None:
            self.are_equal(
                cpu.cores_logical,
                system_logical,
                f'API logical cores ({cpu.cores_logical}) != system logical cores ({system_logical})'
            )
        
        if cpu.cores_physical is not None:
            self.is_true(
                1 <= cpu.cores_physical <= cpu.cores_logical,
                'Physical cores must be <= logical cores and >= 1'
            )
        
        system_freq = self._read_cpu_freq_from_proc()

        if cpu.freq is not None and system_freq is not None:
            # Normalne odchyłki (idle, governor) ± 300 MHz
            self.is_true(
                abs(cpu.freq - system_freq) < 300,
                f'API CPU freq ({cpu.freq}) too far from system freq ({system_freq})'
            )
        
        if cpu.freq_min is not None and cpu.freq_max is not None:
            self.is_true(
                cpu.freq_min <= cpu.freq_max,
                'freq_min cannot be greater than freq_max'
            )

if __name__ == '__main__':
    TestSystemInfoCpu().run()