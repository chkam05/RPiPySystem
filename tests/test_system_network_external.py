import ipaddress
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.network.external.external_network_info import ExternalNetworkInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemInfoNetworkExternal(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_external_network(self) -> ExternalNetworkInfo:
        # Make request
        resp = self.client.get('/network/external', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, dict)

        # Model mapping
        info = ExternalNetworkInfo.from_dict(data)
        self.is_instance_of_type(info, ExternalNetworkInfo, f'Response is not an instance of ExternalNetworkInfo.')

        return info

    def _get_external_ip_from_service(self) -> str | None:
        """
        Attempts to retrieve an external IP address from a popular service. 
        Returns the IP as a string or None if unsuccessful (no internet connection, etc.).
        """
        commands = [
            ['curl', '-s', 'https://api.ipify.org'],
            ['curl', '-s', 'https://ifconfig.me'],
        ]

        for cmd in commands:
            try:
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=5,
                    check=False,
                )
            except Exception:
                continue

            out = (proc.stdout or '').strip()
            if not out:
                continue

            # Verifying that this is a valid IP:
            try:
                ipaddress.ip_address(out)
                return out
            except ValueError:
                continue

        return None

    @testcase
    def test_01_external_basic_shape(self) -> None:
        info = self._get_external_network()
        
        self.is_instance_of_type(info.address, str)
        self.is_not_empty(info.address)

        try:
            ip = ipaddress.ip_address(info.address)
        except ValueError:
            self.fail(f'API returned invalid IP address: {info.address!r}')
            return
    
        self.is_false(ip.is_unspecified, 'IP address cannot be unspecified (0.0.0.0 / ::)')
    
    @testcase
    def test_02_external_is_public_ip(self) -> None:
        info = self._get_external_network()

        try:
            ip = ipaddress.ip_address(info.address)
        except ValueError:
            self.fail(f'API returned invalid IP address: {info.address!r}')
            return

        # /api/system/network/external is supposed to return the "external" address,
        # so it shouldn't be:
        # - private (192.168.x.x, 10.x.x.x, 172.16–31.x.x / fc00::/7),
        # - loopback (127.0.0.1 / ::1),
        # - link-local, multicast etc.
        self.is_false(ip.is_private, f'External IP should not be private: {ip!r}.')
        self.is_false(ip.is_loopback, f'External IP should not be loopback: {ip!r}.')
        self.is_false(ip.is_link_local, f'External IP should not be link-local: {ip!r}.')
        self.is_false(ip.is_multicast, f'External IP should not be multicast: {ip!r}.')

    @testcase
    def test_03_external_matches_external_service(self) -> None:
        info = self._get_external_network()

        # Try to get IP from an external service – if it fails,
        # simply completes the test without assertion (to avoid flaky results).
        external_ip = self._get_external_ip_from_service()
        if external_ip is None:
            # No internet / no curl / whatever - skip comparison.
            return

        # If successful, the IP should be identical to the one from the API.
        self.are_equal(
            info.address,
            external_ip,
            f"External IP from API ({info.address!r}) does not match IP from external service ({external_ip!r})"
        )


if __name__ == '__main__':
    TestSystemInfoNetworkExternal().run()