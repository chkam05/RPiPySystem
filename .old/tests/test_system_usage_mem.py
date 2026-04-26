import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.usage.mem_usage import MemUsage
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemMemUsage(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_mem_usage(self) -> MemUsage:
        # Make request
        resp = self.client.get('/usage/memory', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, dict)

        # Model mapping
        usage = MemUsage.from_dict(data)
        self.is_instance_of_type(usage, MemUsage, f'Response is not an instance of MemUsage.')

        return usage
    
    def _read_meminfo(self) -> dict[str, int]:
        """
        Parses /proc/meminfo into a dictionary:
        { 'MemTotal': <kB:int>, 'MemFree': <kB:int>, ... }
        """
        path = '/proc/meminfo'
        if not os.path.exists(path):
            return {}

        result: dict[str, int] = {}

        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    key, rest = line.split(':', 1)
                    parts = rest.strip().split()
                    if not parts:
                        continue
                    # The first element is a number in kB.
                    try:
                        value_kb = int(parts[0])
                    except ValueError:
                        continue
                    result[key] = value_kb
        except Exception:
            return {}

        return result

    @testcase
    def test_01_memusage_basic_shape(self) -> None:
        usage = self._get_mem_usage()

        # All fields, if not None, should be >= 0 (MB).
        for field_name in (
            MemUsage.FIELD_TOTAL,
            MemUsage.FIELD_FREE,
            MemUsage.FIELD_USED,
            MemUsage.FIELD_AVAILABLE,
            MemUsage.FIELD_BUFF_CACHE,
            MemUsage.FIELD_SHARED,
            MemUsage.FIELD_SWAP_TOTAL,
            MemUsage.FIELD_SWAP_FREE,
            MemUsage.FIELD_SWAP_USED,
            MemUsage.FIELD_SUM_TOTAL,
            MemUsage.FIELD_SUM_FREE,
            MemUsage.FIELD_SUM_USED
        ):
            value = getattr(usage, field_name)
            if value is not None:
                self.is_instance_of_type(value, int)
                self.is_true(
                    value >= 0,
                    f'{field_name} must be >= 0, got {value}'
                )

        # --- Simple field relationships ---

        # total >= free / used / available (if all exist).
        if usage.total is not None and usage.free is not None:
            self.is_true(
                usage.total >= usage.free,
                f'total ({usage.total}) < free ({usage.free})'
            )

        if usage.total is not None and usage.used is not None:
            self.is_true(
                usage.total >= usage.used,
                f'total ({usage.total}) < used ({usage.used})'
            )

        if usage.total is not None and usage.available is not None:
            self.is_true(
                usage.total >= usage.available,
                f'total ({usage.total}) < available ({usage.available})'
            )

        # swap_total >= swap_free / swap_used
        if usage.swap_total is not None and usage.swap_free is not None:
            self.is_true(
                usage.swap_total >= usage.swap_free,
                f'swap_total ({usage.swap_total}) < swap_free ({usage.swap_free})'
            )

        if usage.swap_total is not None and usage.swap_used is not None:
            self.is_true(
                usage.swap_total >= usage.swap_used,
                f'swap_total ({usage.swap_total}) < swap_used ({usage.swap_used})'
            )

        # sum_total ≈ total + swap_total (if everything is available).
        if (
            usage.sum_total is not None and
            usage.total is not None and
            usage.swap_total is not None
        ):
            expected_sum = usage.total + usage.swap_total
            diff = abs(usage.sum_total - expected_sum)
            tol = max(10, int(expected_sum * 0.1))  # 10% or min. 10 MB

            self.is_true(
                diff <= tol,
                f'sum_total ({usage.sum_total}) is not close to total+swap_total '
                f'({expected_sum}) with tol={tol}'
            )

        # sum_free ≈ free + swap_free
        if (
            usage.sum_free is not None and
            usage.free is not None and
            usage.swap_free is not None
        ):
            expected_sum_free = usage.free + usage.swap_free
            diff = abs(usage.sum_free - expected_sum_free)
            tol = max(10, int(expected_sum_free * 0.1))

            self.is_true(
                diff <= tol,
                f'sum_free ({usage.sum_free}) is not close to free+swap_free '
                f'({expected_sum_free}) with tol={tol}'
            )
    
    @testcase
    def test_02_memusage_matches_system(self) -> None:
        usage = self._get_mem_usage()

        meminfo = self._read_meminfo()
        # If /proc/meminfo doesn't exist, something is very strange, but let the test mark it.
        self.is_true(bool(meminfo), '/proc/meminfo is empty or missing')

        # Convert to MB (kB // 1024).
        def kb_to_mb(key: str) -> int | None:
            if key not in meminfo:
                return None
            try:
                return meminfo[key] // 1024
            except Exception:
                return None

        mem_total_mb = kb_to_mb('MemTotal')
        mem_free_mb = kb_to_mb('MemFree')
        mem_avail_mb = kb_to_mb('MemAvailable')
        swap_total_mb = kb_to_mb('SwapTotal')
        swap_free_mb = kb_to_mb('SwapFree')

        # Total vs MemTotal
        if usage.total is not None and mem_total_mb is not None:
            tol = max(20, int(mem_total_mb * 0.1))  # 10% or min. 20 MB
            diff = abs(usage.total - mem_total_mb)
            self.is_true(
                diff <= tol,
                f'total from API ({usage.total} MB) differs too much from MemTotal ({mem_total_mb} MB) tol={tol}'
            )

        #   Free vs MemFree
        if usage.free is not None and mem_free_mb is not None:
            tol = max(20, int(mem_free_mb * 0.2))  # 20% because free is changing quickly.
            diff = abs(usage.free - mem_free_mb)
            self.is_true(
                diff <= tol,
                f'free from API ({usage.free} MB) differs too much from MemFree ({mem_free_mb} MB) tol={tol}'
            )

        #   Available vs MemAvailable
        if usage.available is not None and mem_avail_mb is not None:
            tol = max(20, int(mem_avail_mb * 0.2))
            diff = abs(usage.available - mem_avail_mb)
            self.is_true(
                diff <= tol,
                f'available from API ({usage.available} MB) differs too much from MemAvailable ({mem_avail_mb} MB) tol={tol}'
            )

        #   Swap_total vs SwapTotal
        if usage.swap_total is not None and swap_total_mb is not None:
            tol = max(10, int(swap_total_mb * 0.1))
            diff = abs(usage.swap_total - swap_total_mb)
            self.is_true(
                diff <= tol,
                f'swap_total from API ({usage.swap_total} MB) differs too much from SwapTotal ({swap_total_mb} MB) tol={tol}'
            )

        #   Swap_free vs SwapFree
        if usage.swap_free is not None and swap_free_mb is not None:
            tol = max(10, int(swap_free_mb * 0.2))
            diff = abs(usage.swap_free - swap_free_mb)
            self.is_true(
                diff <= tol,
                f'swap_free from API ({usage.swap_free} MB) differs too much from SwapFree ({swap_free_mb} MB) tol={tol}'
            )


if __name__ == '__main__':
    TestSystemMemUsage().run()