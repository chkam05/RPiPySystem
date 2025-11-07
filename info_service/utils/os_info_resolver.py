from datetime import datetime
import re
import subprocess
from typing import ClassVar, Dict, Optional

from info_service.models.system.os_info import OSInfo


class OSInfoResolver:
    """
    Static utility for resolving OS information.
    """

    # --- Regex ClassVars ---
    RE_UNAME_V_DATE: ClassVar[str] = r'\((\d{4}-\d{2}-\d{2})\)'
    RE_DEBIAN_KERNEL_VER: ClassVar[str] = r'\bDebian\s+([0-9][0-9A-Za-z:.\-+~]+)'
    RE_KERNEL_VER_GENERIC_BEFORE_PAREN: ClassVar[str] = r'([0-9]+:[0-9A-Za-z:.\-+~]+)(?=\s*\()'

    # --- File paths ---
    OS_RELEASE_PATH: ClassVar[str] = '/etc/os-release'


    def __new__(cls, *args, **kwargs):
        """
        Prevent instantiation of this static utility class.
        """
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')
    

    # --------------------------------------------------------------------------
    # --- GLOBAL HELPERS (Generic for future extensions). ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _run_cmd(args: list[str]) -> Optional[str]:
        """
        Run a command and return stdout.
        """
        try:
            out = subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL)
            return out.strip() if out else None
        except Exception:
            return None
    
    @staticmethod
    def _read_text(path: str) -> Optional[str]:
        """
        Read a text file and return content.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    @staticmethod
    def _parse_kv_file(content: Optional[str]) -> Dict[str, str]:
        """
        Parse simple KEY=VALUE lines into dict.
        """
        result: Dict[str, str] = {}

        if not content:
            return result
        
        for line in content.splitlines():
            line = line.strip()
            if not line or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"')
            result[k] = v
        return result
    
    @classmethod
    def _re_search(cls, pattern: str, text: Optional[str], group: int = 1) -> Optional[str]:
        """
        Search regex and return group.
        """
        if not text:
            return None
        m = re.search(pattern, text)
        return m.group(group) if m else None
    

    # --------------------------------------------------------------------------
    # --- GET OPERATING SYSTEM INFO ---
    # --------------------------------------------------------------------------

    @classmethod
    def _parse_uname_date(cls, uname_v: Optional[str]) -> Optional[datetime]:
        """
        Extract compilation date from uname -v.
        """
        date_str = cls._re_search(cls.RE_UNAME_V_DATE, uname_v)
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, OSInfo.DATETIME_FORMAT)
        except (TypeError, ValueError):
            return None
    
    @classmethod
    def _parse_kernel_pkgver(cls, uname_v: Optional[str]) -> Optional[str]:
        """
        Extract kernel package version from uname -v.
        """
        if not uname_v:
            return None
        # Prefer explicit 'Debian <pkgver>' pattern
        ver = cls._re_search(cls.RE_DEBIAN_KERNEL_VER, uname_v)
        if ver:
            return ver
        # Fallback: token like 'epoch:version-rev' before '(YYYY-MM-DD)'
        return cls._re_search(cls.RE_KERNEL_VER_GENERIC_BEFORE_PAREN, uname_v)
    
    @staticmethod
    def get_os_info() -> OSInfo:
        """
        Collect and return OSInfo from system.
        """
        # /etc/os-release
        os_release_text = OSInfoResolver._read_text(OSInfoResolver.OS_RELEASE_PATH)
        os_release = OSInfoResolver._parse_kv_file(os_release_text)

        # uname values
        uname_r = OSInfoResolver._run_cmd(['uname', '-r'])  # e.g. '6.12.47+rpt-rpi-v8'
        uname_s = OSInfoResolver._run_cmd(['uname', '-s'])  # e.g. 'Linux'
        uname_o = OSInfoResolver._run_cmd(['uname', '-o'])  # e.g. 'GNU/Linux'
        uname_v = OSInfoResolver._run_cmd(['uname', '-v'])  # e.g. '#1 SMP PREEMPT Debian 1:6... (YYYY-MM-DD)'
        uname_m = OSInfoResolver._run_cmd(['uname', '-m'])  # e.g. 'aarch64'
        uname_n = OSInfoResolver._run_cmd(['uname', '-n'])  # e.g. 'raspberrypi'

        return OSInfo(
            distribution=os_release.get('NAME'),
            distribution_codename=os_release.get('VERSION_CODENAME'),
            distribution_version=os_release.get('DEBIAN_VERSION_FULL'),
            kernel=uname_s,
            kernel_name=uname_o,
            kernel_version=OSInfoResolver._parse_kernel_pkgver(uname_v),  # '1:6.12.47-1+rpt1'
            release_version=uname_r,  # '6.12.47+rpt-rpi-v8'
            architecture=uname_m,
            compilation_date=OSInfoResolver._parse_uname_date(uname_v),
            network_name=uname_n
        )