from __future__ import annotations
from datetime import datetime
from email.utils import parsedate_to_datetime
import platform

from core.system.models.os_info import OSInfo
from core.system.utilities._helpers import hostname, parse_os_release


class OSInfoUtility:
    def get_info(self) -> OSInfo:
        release = parse_os_release()
        uname = platform.uname()
        return OSInfo(
            distribution=release.get('PRETTY_NAME') or release.get('NAME'),
            distribution_codename=release.get('VERSION_CODENAME'),
            distribution_version=release.get('VERSION_ID'),
            kernel=uname.system or None,
            kernel_name=release.get('ID_LIKE') or release.get('ID'),
            kernel_version=uname.version or None,
            release_version=uname.release or None,
            architecture=uname.machine or None,
            compilation_date=self._parse_kernel_compilation_date(uname.version),
            network_name=hostname(),
        )

    def _parse_kernel_compilation_date(self, version: str) -> datetime | None:
        parts = version.split()
        for index in range(len(parts)):
            candidate = ' '.join(parts[index:index + 5])
            try:
                return parsedate_to_datetime(candidate)
            except (TypeError, ValueError, IndexError):
                continue

        return None
