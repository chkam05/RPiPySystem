from __future__ import annotations
import socket
import requests

from core.system.models.external_network_info import ExternalNetworkInfo
from core.system.enums.interface_channel import InterfaceChannel
from core.system.enums.interface_device import InterfaceDevice
from core.system.enums.interface_flag import InterfaceFlag
from core.system.models.interface_info import InterfaceInfo
from core.system.models.interface_scope_id import InterfaceScopeId
from core.system.models.interface_statistics import InterfaceStatistics
from core.system.utilities._helpers import psutil


class NetworkInfoUtility:
    EXTERNAL_IP_URL = 'https://api.ipify.org'

    def get_interfaces(self) -> list[InterfaceInfo]:
        if not psutil:
            return []

        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        interfaces: list[InterfaceInfo] = []

        for name, addresses in addrs.items():
            interfaces.append(self._interface_from_data(
                name=name,
                addresses=addresses,
                stat=stats.get(name),
                counters=io_counters.get(name),
            ))

        return interfaces

    def get_interface(self, name: str) -> InterfaceInfo | None:
        if not psutil:
            return None

        addrs = psutil.net_if_addrs()
        addresses = addrs.get(name)
        if addresses is None:
            return None

        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        return self._interface_from_data(
            name=name,
            addresses=addresses,
            stat=stats.get(name),
            counters=io_counters.get(name),
        )

    def get_external_info(self, timeout: float = 2.0) -> ExternalNetworkInfo | None:
        try:
            response = requests.get(self.EXTERNAL_IP_URL, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException:
            return None

        address = response.text.strip()
        return ExternalNetworkInfo(address=address) if address else None

    def _interface_from_data(self, name: str, addresses, stat, counters) -> InterfaceInfo:
        interface = InterfaceInfo(
            network=name,
            flags=self._flags(stat.flags if stat else ''),
            flags_bin=0,
            mtu=stat.mtu if stat else 0,
            device=self._device(name),
            statistics=self._statistics(counters),
        )

        for address in addresses:
            if address.family == socket.AF_INET:
                interface.inet = address.address
                interface.netmask = address.netmask
                interface.broadcast = address.broadcast
            elif address.family == socket.AF_INET6:
                interface.inet6 = address.address.split('%', 1)[0]
                interface.prefixlen = self._prefixlen(address.netmask)
                interface.scopeid = self._scopeid(address.address)
            elif self._is_link_address(address.family):
                interface.ether = address.address

        return interface

    def _statistics(self, counters) -> list[InterfaceStatistics]:
        if counters is None:
            return []

        return [
            InterfaceStatistics(
                channel=InterfaceChannel.RX,
                packets=counters.packets_recv,
                bytes=counters.bytes_recv,
                errors=counters.errin,
                dropped=counters.dropin,
            ),
            InterfaceStatistics(
                channel=InterfaceChannel.TX,
                packets=counters.packets_sent,
                bytes=counters.bytes_sent,
                errors=counters.errout,
                dropped=counters.dropout,
            ),
        ]

    def _flags(self, flags: str) -> list[InterfaceFlag]:
        result: list[InterfaceFlag] = []
        for flag in (flags or '').split(','):
            try:
                result.append(InterfaceFlag.from_str(flag.strip().replace('_', '-')))
            except ValueError:
                continue

        return result

    def _device(self, name: str) -> InterfaceDevice:
        if name == 'lo':
            return InterfaceDevice.LOOPBACK
        if name.startswith(('eth', 'en')):
            return InterfaceDevice.ETHERNET
        if name.startswith(('wlan', 'wl')):
            return InterfaceDevice.WI_FI_RADIOTAP
        if name.startswith('br'):
            return InterfaceDevice.BRIDGE
        if name.startswith('bond'):
            return InterfaceDevice.BOND
        if '.' in name:
            return InterfaceDevice.VLAN

        return InterfaceDevice.UNSPEC

    def _prefixlen(self, netmask: str | None) -> int | None:
        if not netmask:
            return None
        if netmask.isdigit():
            return int(netmask)

        try:
            return sum(bin(int(part, 16)).count('1') for part in netmask.split(':') if part)
        except ValueError:
            return None

    def _scopeid(self, address: str) -> InterfaceScopeId | None:
        if address.startswith('fe80:'):
            return InterfaceScopeId.LINK
        if address == '::1':
            return InterfaceScopeId.HOST
        if address:
            return InterfaceScopeId.GLOBAL

        return None

    def _is_link_address(self, family) -> bool:
        return family == getattr(psutil, 'AF_LINK', object()) or family == getattr(socket, 'AF_PACKET', object())
