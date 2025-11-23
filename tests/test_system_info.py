from datetime import datetime
import platform
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.info.os_info import OSInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemInfo(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_info(self) -> OSInfo:
        # Make request
        resp = self.client.get('/info/', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_instance_of_type(data, dict)
        self.is_not_empty(data)

        # Model mapping
        os_info = OSInfo.from_dict(data)
        self.is_instance_of_type(os_info, OSInfo, f'Response is not an instance of OSInfo.')

        return os_info

    @testcase
    def test_01_info_basic_shape(self) -> None:
        os_info = self._get_info()

        # Build - should be in the past (if set).
        if os_info.compilation_date is not None:
            self.is_instance_of_type(os_info.compilation_date, datetime)
            now = datetime.now(os_info.compilation_date.tzinfo)
            self.is_true(os_info.compilation_date <= now, 'Compilation date is in the future')

        # Distribution - if present, then non-empty.
        if os_info.distribution is not None:
            self.is_instance_of_type(os_info.distribution, str)
            self.is_not_empty(os_info.distribution)
        
        # Architecture – if it exists, it is not empty.
        if os_info.architecture is not None:
            self.is_instance_of_type(os_info.architecture, str)
            self.is_not_empty(os_info.architecture)
        
        # Network name - if present, not empty
        if os_info.network_name is not None:
            self.is_instance_of_type(os_info.network_name, str)
            self.is_not_empty(os_info.network_name)
    
    @testcase
    def test_02_info_matches_system(self) -> None:
        os_info = self._get_info()

        # Getting information directly from the system.
        uname = platform.uname()
        hostname = socket.gethostname()

        # --- kernel/system ---
        # On Linux, uname.system should be "Linux" – this can be safely enforced.
        if os_info.kernel is not None:
            self.are_equal(
                os_info.kernel,
                uname.system,
                f'Kernel from API ({os_info.kernel!r}) does not match system uname ({uname.system!r}).'
            )
        
        # --- architecture ---
        if os_info.architecture is not None:
            # najczęściej będzie to samo co uname.machine, np. 'aarch64'
            self.are_equal(
                os_info.architecture,
                uname.machine,
                f'Architecture from API ({os_info.architecture!r}) does not match uname.machine ({uname.machine!r})'
            )
        
        # --- network name / hostname ---
        if os_info.network_name is not None:
            # zależnie od implementacji możesz mieć dokładnie hostname albo np. krótszą wersję
            # tutaj zakładamy, że powinno być równe gethostname()
            self.are_equal(
                os_info.network_name,
                hostname,
                f'Network name from API ({os_info.network_name!r}) does not match socket.gethostname() ({hostname!r})'
            )

if __name__ == '__main__':
    TestSystemInfo().run()