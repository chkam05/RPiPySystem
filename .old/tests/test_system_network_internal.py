import ipaddress
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List

from system_service.models.network.internal.interface_statistics import InterfaceStatistics

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.network.internal.interface_device import InterfaceDevice
from system_service.models.network.internal.interface_flag import InterfaceFlag
from system_service.models.network.internal.interface_info import InterfaceInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class ExampleTest(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_response(self) -> List[InterfaceInfo]:
        # Make request
        resp = self.client.get('/network/internal/list', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, list)

        # Model mapping
        interfaces = InterfaceInfo.from_list_dicts(data)
        self.is_instance_of_type(interfaces, list, f'Response is not an instance of InterfaceInfo list.')

        return interfaces

    def _get_system_interfaces(self):
        """Returns the result of `ip -j addr` as a list of dictionaries."""
        try:
            proc = subprocess.run(
                ['ip', '-j', 'addr'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False
            )
        except Exception:
            return []

        try:
            return json.loads(proc.stdout)
        except Exception:
            return []

    def _extract_ipv4(self, iface_dict):
        for addr in iface_dict.get('addr_info', []):
            if addr.get('family') == 'inet':
                return addr.get('local')
        return None

    def _extract_ipv6(self, iface_dict):
        for addr in iface_dict.get('addr_info', []):
            if addr.get('family') == 'inet6':
                return addr.get('local')
        return None

    @testcase
    def test_01_interfaces_basic_shape(self) -> None:
        interfaces = self._get_response()

        iface = interfaces[0]
        self.is_instance_of_type(iface, InterfaceInfo, 'Item in list is not an instance of InterfaceInfo.')

        # --- required fields ---
        self.is_instance_of_type(iface.network, str)
        self.is_not_empty(iface.network)

        self.is_instance_of_type(iface.flags, list)
        for f in iface.flags:
            self.is_instance_of_type(f, InterfaceFlag)
        
        self.is_instance_of_type(iface.flags_bin, int)
        self.is_true(iface.flags_bin >= 0)

        self.is_instance_of_type(iface.mtu, int)
        self.is_true(iface.mtu > 0)

        self.is_instance_of_type(iface.device, InterfaceDevice)

         # statistics
        self.is_instance_of_type(iface.statistics, list)
        self.is_not_empty(iface.statistics)

        for st in iface.statistics:
            self.is_instance_of_type(st, InterfaceStatistics)
            self.is_instance_of_type(st.channel.value, str)

            if st.packets is not None:
                self.is_true(st.packets >= 0)

            if st.bytes is not None:
                self.is_true(st.bytes >= 0)

            for field in (st.errors, st.dropped, st.overruns, st.frame, st.carrier, st.collisions):
                if field is not None:
                    self.is_true(field >= 0)
        
        # --- optional fields ---
        if iface.inet is not None:
            try:
                ipaddress.ip_address(iface.inet)
            except ValueError:
                self.fail(f'Invalid IPv4 address in API: {iface.inet!r}.')

        if iface.inet6 is not None:
            try:
                ipaddress.ip_address(iface.inet6)
            except ValueError:
                self.fail(f'Invalid IPv6 address in API: {iface.inet6!r}.')

        if iface.txqueuelen is not None:
            self.is_true(iface.txqueuelen >= 0)
    
    @testcase
    def test_02_interfaces_match_system(self) -> None:
        interfaces = self._get_response()

        # pobierz rzeczywiste interfejsy z systemu
        sys_ifaces = self._get_system_interfaces()
        self.is_true(bool(sys_ifaces), 'System has no network interfaces?')

        # mapowanie po nazwie
        sys_map = {i['ifname']: i for i in sys_ifaces}

        checked = 0

        for iface in interfaces:
            name = iface.network

            if name not in sys_map:
                # Some interfaces (e.g. tunl0, ip6tnl0) the backend can filter.
                continue

            sys_if = sys_map[name]

            # MTU
            if 'mtu' in sys_if:
                self.are_equal(
                    iface.mtu,
                    sys_if['mtu'],
                    f'MTU mismatch for interface {name}.'
                )

            # MAC address
            if iface.ether is not None and 'address' in sys_if:
                # sys_if['address] may not exist for virtual interfaces.
                if sys_if['address']:
                    self.are_equal(
                        iface.ether.lower(),
                        sys_if['address'].lower(),
                        f'MAC address mismatch for interface {name}.'
                    )

            # IPv4
            if iface.inet is not None:
                sys_ipv4 = self._extract_ipv4(sys_if)
                if sys_ipv4:
                    self.are_equal(
                        iface.inet,
                        sys_ipv4,
                        f'IPv4 mismatch for interface {name}.'
                    )

            # IPv6
            if iface.inet6 is not None:
                sys_ipv6 = self._extract_ipv6(sys_if)
                if sys_ipv6:
                    # Some IPv6 have suffixes (scope), so we compare the beginning.
                    self.is_true(
                        sys_ipv6.startswith(iface.inet6) or iface.inet6.startswith(sys_ipv6),
                        f'IPv6 mismatch for interface {name}.'
                    )

            # Flags
            if 'flags' in sys_if:
                sys_flags = set(sys_if['flags'])
                api_flags = {f.value for f in iface.flags}

                # Basic flags that *if* appear in the API,
                # these must also occur in the system
                important = {'UP', 'LOOPBACK', 'BROADCAST', 'MULTICAST'}
                required = important & api_flags

                for fl in required:
                    self.is_true(
                        fl in sys_flags,
                        f'Flag "{fl}" present in API but not in system flags {sys_flags} for {name}.'
                    )

                # Additionally: flag sets cannot be completely destroyed.
                # Require at least one common flag.
                common = api_flags & sys_flags
                self.is_true(
                    len(common) > 0,
                    f'API flags {api_flags} have no overlap with system flags {sys_flags} for {name}.'
                )

            checked += 1

            if checked >= 8:    # Don't test dozens of interfaces.
                break

        self.is_true(checked > 0, 'No interfaces could be validated against system.')
    
    @testcase
    def test_03_interfaces_statistics_match_system(self) -> None:
        interfaces = self._get_response()

        for iface in interfaces:
            name = iface.network

            rx_path = f'/sys/class/net/{name}/statistics/rx_bytes'
            tx_path = f'/sys/class/net/{name}/statistics/tx_bytes'

            if not (os.path.exists(rx_path) and os.path.exists(tx_path)):
                continue

            try:
                with open(rx_path) as f:
                    sys_rx_bytes = int(f.read().strip())

                with open(tx_path) as f:
                    sys_tx_bytes = int(f.read().strip())
            except Exception:
                continue

            # Statistics from API
            rx = next((s for s in iface.statistics if s.channel.value == "RX"), None)
            tx = next((s for s in iface.statistics if s.channel.value == "TX"), None)

            # --- RX ---
            if rx and rx.bytes is not None:
                # Allow for a deviation of ± a few percent (because the movement is ongoing).
                self.is_true(
                    abs(rx.bytes - sys_rx_bytes) < max(5000, sys_rx_bytes * 0.05),
                    f'RX bytes mismatch for {name}: API={rx.bytes}, sys={sys_rx_bytes}.'
                )

            # --- TX ---
            if tx and tx.bytes is not None:
                self.is_true(
                    abs(tx.bytes - sys_tx_bytes) < max(5000, sys_tx_bytes * 0.05),
                    f'TX bytes mismatch for {name}: API={tx.bytes}, sys={sys_tx_bytes}.'
                )


if __name__ == '__main__':
    ExampleTest().run()