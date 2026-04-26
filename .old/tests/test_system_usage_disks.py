import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.usage.disk_type import DiskType
from system_service.models.system.usage.disk_usage import DiskUsage
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM
from utils.models.public_model import PublicModel


class TestSystemUsageDisks(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_disks_usage(self) -> PublicModel:
        # Make request
        resp = self.client.get('/usage/disks', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, list)

        # Model mapping
        disks = DiskUsage.from_list_dicts(data)
        self.is_instance_of_type(disks, list, f'Response is not an instance of DiskUsage list.')

        return disks

    def _get_df_entries(self) -> list[dict]:
        """
        Returns a list of dictionaries:
        {
            'filesystem: <str>,
            'size_kb: <int>,
            'used_kb: <int>,
            'avail_kb: <int>,
            'mount_point: <str>,
        }
        based on `df -P`.
        """
        try:
            proc = subprocess.run(
                ['df', '-P'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
        except Exception:
            return []

        lines = (proc.stdout or '').splitlines()
        if len(lines) <= 1:
            return []

        entries: list[dict] = []

        # Skip the headline:
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            # Typical format: Filesystem 1024-blocks Used Available Capacity Mounted-on.
            if len(parts) < 6:
                # Sometimes the filesystem name is complex and breaks into several fields,
                # but then mount_point is always the last field, and size/used/avail just before.
                continue

            filesystem = parts[0]
            try:
                size_kb = int(parts[1])
                used_kb = int(parts[2])
                avail_kb = int(parts[3])
            except ValueError:
                continue

            mount_point = parts[-1]

            entries.append({
                'filesystem': filesystem,
                'size_kb': size_kb,
                'used_kb': used_kb,
                'avail_kb': avail_kb,
                'mount_point': mount_point,
            })

        return entries

    @testcase
    def test_01_disks_basic_shape(self) -> None:
        disks = self._get_disks_usage()
        disk: DiskUsage = disks[0]
        self.is_instance_of_type(disk, DiskUsage)

        # dev_name – required, non-empty string.
        self.is_instance_of_type(disk.dev_name, str)
        self.is_not_empty(disk.dev_name)

        # fs_type – valid DiskType enum.
        self.is_instance_of_type(disk.fs_type, DiskType)

        # label/uuid – optional strings.
        if disk.label is not None:
            self.is_instance_of_type(disk.label, str)

        if disk.uuid is not None:
            self.is_instance_of_type(disk.uuid, str)

        # size/free/used – if exists, non-negative.
        for val, name in (
            (disk.size_mb, 'size_mb'),
            (disk.free_mb, 'free_mb'),
            (disk.used_mb, 'used_mb'),
        ):
            if val is not None:
                self.is_instance_of_type(val, int)
                self.is_true(val >= 0, f'{name} must be >= 0')

        # mount_point – ooptional string (e.g. '/', '/boot', '[SWAP]').
        if disk.mount_point is not None:
            self.is_instance_of_type(disk.mount_point, str)
            self.is_not_empty(disk.mount_point)

        # If there is a complete set of numbers, check the simple relationship:
        # used_mb + free_mb ≈ size_mb (with some tolerance).
        if disk.size_mb is not None and disk.free_mb is not None and disk.used_mb is not None:
            calculated = disk.free_mb + disk.used_mb
            # Due to rounding and on-the-fly variations, a 5% tolerance is used.
            tolerance = max(10, int(disk.size_mb * 0.05))

            self.is_true(
                abs(disk.size_mb - calculated) <= tolerance,
                f'size_mb ({disk.size_mb}) is not close to free_mb+used_mb '
                f'({disk.free_mb}+{disk.used_mb}={calculated}) with tolerance {tolerance}'
            )
    
    @testcase
    def test_02_disks_match_system(self) -> None:
        """
        Compares API results with what `df -P` shows.
        It does not require 1:1 ideal values ​​(because the system is alive),
        but it verifies that at least one filesystem overlaps
        sensibly with system data.
        """
        disks = self._get_disks_usage()

        # Get information with df -P (POSIX, stable format).
        df_entries = self._get_df_entries()
        self.is_true(bool(df_entries), '`df -P` returned no entries')

        # mapujemy df po mount_point (ostatnia kolumna)
        df_by_mount = {e['mount_point']: e for e in df_entries}

        checked = 0

        for disk in disks:
            # Skips SWAP disks or no mount_point.
            if disk.mount_point is None or disk.mount_point == '[SWAP]':
                continue

            if disk.mount_point not in df_by_mount:
                # e.g. pseudo-mount or something unusual.
                continue

            df_entry = df_by_mount[disk.mount_point]

            # Values ​​from df are in 1K-blocks, so convert to MB.
            size_mb_sys = df_entry['size_kb'] // 1024
            used_mb_sys = df_entry['used_kb'] // 1024
            avail_mb_sys = df_entry['avail_kb'] // 1024

            # API may sometimes not know the size - if missing, skip this disk.
            if disk.size_mb is None or disk.used_mb is None or disk.free_mb is None:
                continue

            # Tolerance because the system changes (files are saved during the test).
            tol_size = max(50, int(size_mb_sys * 0.1))   # 10% or min. 50 MB
            tol_used = max(50, int(used_mb_sys * 0.1))
            tol_free = max(50, int(avail_mb_sys * 0.1))

            # --- size ---
            self.is_true(
                abs(disk.size_mb - size_mb_sys) <= tol_size,
                f'Size mismatch for {disk.mount_point}: '
                f'API={disk.size_mb} MB, sys={size_mb_sys} MB (tol={tol_size})'
            )

            # --- used ---
            self.is_true(
                abs(disk.used_mb - used_mb_sys) <= tol_used,
                f'Used mismatch for {disk.mount_point}: '
                f'API={disk.used_mb} MB, sys={used_mb_sys} MB (tol={tol_used})'
            )

            # --- free ---
            self.is_true(
                abs(disk.free_mb - avail_mb_sys) <= tol_free,
                f'Free mismatch for {disk.mount_point}: '
                f'API={disk.free_mb} MB, sys={avail_mb_sys} MB (tol={tol_free})'
            )

            checked += 1

            # Don't check all of them, it's important that a few match.
            if checked >= 3:
                break

        self.is_true(checked > 0, 'No disk entries could be validated against `df -P` output')


if __name__ == '__main__':
    TestSystemUsageDisks().run()