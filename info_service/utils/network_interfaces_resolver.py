import re
import subprocess
from typing import ClassVar, List, Optional, Tuple, Pattern

from info_service.models.internal.interface_channel import InterfaceChannel
from info_service.models.internal.interface_device import InterfaceDevice
from info_service.models.internal.interface_flag import InterfaceFlag
from info_service.models.internal.interface_info import InterfaceInfo
from info_service.models.internal.interface_scope_id import InterfaceScopeId
from info_service.models.internal.interface_statistics import InterfaceStatistics


class NetworkInterfacesResolver:
    """
    Static utility that parses `ifconfig` output into structured interface models.
    """

    # Line type tags
    _ERRORS_LINE: ClassVar[str] = 'errors'
    _HEADER_LINE: ClassVar[str] = 'header'
    _IPV4_LINE: ClassVar[str] = 'ipv4'
    _IPV6_LINE: ClassVar[str] = 'ipv6'
    _META_LINE: ClassVar[str] = 'meta'
    _OTHER_LINE: ClassVar[str] = 'other'
    _RX_LINE: ClassVar[str] = 'rx_packets'
    _TX_LINE: ClassVar[str] = 'tx_packets'

    # Command name (can be overridden for testing)
    _IFCONFIG_CMD: ClassVar[List[str]] = ['ifconfig']

    # Defaults
    _DEFAULT_MTU: ClassVar[int] = 1500

    # Regex patterns (precompiled)
    _RE_HEADER: ClassVar[Pattern[str]] = re.compile(r'^\S+:\s+flags=\d+<[^>]+>\s+mtu\s+\d+')
    _RE_HEADER_GROUPS: ClassVar[Pattern[str]] = re.compile(r'^(\S+):\s+flags=(\d+)\<([^>]*)\>\s+mtu\s+(\d+)')
    _RE_IPV4: ClassVar[Pattern[str]] = re.compile(r'\binet\s+(\S+)(?:\s+netmask\s+(\S+))?(?:\s+broadcast\s+(\S+))?')
    _RE_IPV6: ClassVar[Pattern[str]] = re.compile(
        r'\binet6\s+(\S+)(?:\s+prefixlen\s+(\d+))?(?:\s+scopeid\s+0x([0-9a-fA-F]+)<([^>]+)>)?'
    )
    _RE_RX_PKTS: ClassVar[Pattern[str]] = re.compile(r'\bRX packets\s+(\d+)\s+bytes\s+(\d+)', re.IGNORECASE)
    _RE_TX_PKTS: ClassVar[Pattern[str]] = re.compile(r'\bTX packets\s+(\d+)\s+bytes\s+(\d+)', re.IGNORECASE)
    _RE_ERRORS: ClassVar[Pattern[str]] = re.compile(
        r'\b([RT]X)\s+errors\s+(\d+)\s+dropped\s+(\d+)\s+overruns\s+(\d+)'
        r'(?:\s+frame\s+(\d+))?(?:\s+carrier\s+(\d+))?(?:\s+collisions\s+(\d+))?',
        re.IGNORECASE,
    )
    _RE_MAC: ClassVar[Pattern[str]] = re.compile(r'\bether\s+([0-9a-fA-F:]{11,17})')
    _RE_TXQLEN: ClassVar[Pattern[str]] = re.compile(r'\btxqueuelen\s+(\d+)', re.IGNORECASE)
    _RE_DEV_LABEL: ClassVar[Pattern[str]] = re.compile(r'\(([^()]+)\)\s*$')

    def __new__(cls, *args, **kwargs):
        """
        Prevent instantiation of this static utility class.
        """
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')
    
    # --------------------------------------------------------------------------
    # --- DATA LINE CLASSIFICATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def _classify_line(cls, line: str) -> str:
        """
        Classify a raw `ifconfig` line into a semantic category.
        """
        if cls._RE_HEADER.search(line):
            return cls._HEADER_LINE
        if 'inet6 ' in line:
            return cls._IPV6_LINE
        if cls._RE_IPV4.search(line) and 'inet6' not in line:
            return cls._IPV4_LINE
        if 'RX packets' in line:
            return cls._RX_LINE
        if 'TX packets' in line:
            return cls._TX_LINE
        if re.search(r'\b[RT]X\s+errors\b', line):
            return cls._ERRORS_LINE
        if 'ether ' in line or 'txqueuelen' in line or cls._RE_DEV_LABEL.search(line):
            return cls._META_LINE
        return cls._OTHER_LINE
    
    # --------------------------------------------------------------------------
    # --- DATA MODEL CREATORS ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _create_interface_info_model() -> InterfaceInfo:
        """
        Create an InterfaceInfo object with safe defaults.
        """
        return InterfaceInfo(
            network='',
            flags=[],
            flags_bin=0,
            mtu=NetworkInterfacesResolver._DEFAULT_MTU,
            device=InterfaceDevice.UNSPEC,
            statistics=[],
            inet=None,
            netmask=None,
            broadcast=None,
            inet6=None,
            prefixlen=None,
            scopeid=None,
            scopeid_int=None,
            ether=None,
            txqueuelen=None,
        )
    
    @staticmethod
    def _create_interface_statistics_model(channel: InterfaceChannel) -> InterfaceStatistics:
        """
        Create an InterfaceStatistics object initialized for the given channel.
        """
        return InterfaceStatistics(
            channel=channel,
            packets=0,
            bytes=0,
            errors=0,
            dropped=0,
            overruns=0,
            frame=0,
            carrier=0,
            collisions=0
        )
    
    # --------------------------------------------------------------------------
    # --- NETWORK INFO LINE DATA PARSERS ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _parse_header_line(info: InterfaceInfo, line: str) -> None:
        """
        Parse interface header line and fill basic fields.
        """
        m = NetworkInterfacesResolver._RE_HEADER_GROUPS.match(line)
        if not m:
            return

        flags_raw = [f.strip() for f in (m.group(3) or '').split(',') if f.strip()]
        parsed = []
        for f in flags_raw:
            try:
                parsed.append(InterfaceFlag.from_str(f))
            except Exception:
                # Ignore unknown flags
                pass

        info.network = m.group(1)
        info.flags_bin = int(m.group(2))
        info.flags = parsed
        info.mtu = int(m.group(4))

    @staticmethod
    def _parse_ipv4_line(info: InterfaceInfo, line: str) -> None:
        """
        Parse IPv4 line and set inet, netmask and broadcast.
        """
        m = NetworkInterfacesResolver._RE_IPV4.search(line)
        if not m:
            return

        info.inet = m.group(1)
        info.netmask = m.group(2) if m.group(2) else None
        info.broadcast = m.group(3) if m.group(3) else None

    @staticmethod
    def _parse_ipv6_line(info: InterfaceInfo, line: str) -> None:
        """
        Parse IPv6 line and choose the most relevant address.
        """
        m = NetworkInterfacesResolver._RE_IPV6.search(line)
        if not m:
            return

        candidate_inet6 = m.group(1)
        candidate_prefixlen = int(m.group(2)) if m.group(2) else None
        candidate_scopeid_int = int(m.group(3), 16) if m.group(3) else None
        candidate_scopeid = None

        if m.group(4):
            try:
                candidate_scopeid = InterfaceScopeId.from_str(m.group(4).strip().upper())
            except Exception:
                candidate_scopeid = InterfaceScopeId.UNKNOWN

        choose = False
        if info.inet6 is None:
            choose = True
        elif info.scopeid != InterfaceScopeId.GLOBAL and candidate_scopeid == InterfaceScopeId.GLOBAL:
            choose = True

        if choose:
            info.inet6 = candidate_inet6
            info.prefixlen = candidate_prefixlen
            info.scopeid_int = candidate_scopeid_int
            info.scopeid = candidate_scopeid

    @staticmethod
    def _parse_meta_line(info: InterfaceInfo, line: str) -> None:
        """
        Parse metadata line (MAC, txqueuelen, device label).
        """
        m_mac = NetworkInterfacesResolver._RE_MAC.search(line)
        if m_mac:
            info.ether = m_mac.group(1).lower()

        m_txq = NetworkInterfacesResolver._RE_TXQLEN.search(line)
        if m_txq:
            info.txqueuelen = int(m_txq.group(1))

        m_dev = NetworkInterfacesResolver._RE_DEV_LABEL.search(line)
        if m_dev:
            label = m_dev.group(1).strip().upper()
            try:
                info.device = InterfaceDevice.from_str(label)
            except Exception:
                info.device = InterfaceDevice.UNSPEC

    # --------------------------------------------------------------------------
    # --- NETWORK STATISTICS LINE DATA PARSERS ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _parse_rx_packets_line(stats: InterfaceStatistics, line: str) -> None:
        """
        Parse RX packets/bytes line into statistics.
        """
        m = NetworkInterfacesResolver._RE_RX_PKTS.search(line)
        if not m:
            return

        stats.packets = int(m.group(1))
        stats.bytes = int(m.group(2))

    @staticmethod
    def _parse_tx_packets_line(stats: InterfaceStatistics, line: str) -> None:
        """
        Parse TX packets/bytes line into statistics.
        """
        m = NetworkInterfacesResolver._RE_TX_PKTS.search(line)
        if not m:
            return

        stats.packets = int(m.group(1))
        stats.bytes = int(m.group(2))

    @staticmethod
    def _parse_error_line(
        rx_stats: Optional[InterfaceStatistics],
        tx_stats: Optional[InterfaceStatistics],
        line: str
    ) -> Tuple[Optional[InterfaceStatistics], Optional[InterfaceStatistics]]:
        """
        Parse RX/TX errors line and merge into the corresponding stats object.
        """
        m = NetworkInterfacesResolver._RE_ERRORS.search(line)
        if not m:
            return rx_stats, tx_stats

        channel = m.group(1).upper()

        if channel == str(InterfaceChannel.RX):
            target = rx_stats or InterfaceStatistics(channel=InterfaceChannel.RX)
            rx_stats = target
        else:
            target = tx_stats or InterfaceStatistics(channel=InterfaceChannel.TX)
            tx_stats = target

        target.errors = int(m.group(2))
        target.dropped = int(m.group(3))
        target.overruns = int(m.group(4))
        target.frame = int(m.group(5)) if m.group(5) else 0
        target.carrier = int(m.group(6)) if m.group(6) else 0
        target.collisions = int(m.group(7)) if m.group(7) else 0

        return rx_stats, tx_stats

    # --------------------------------------------------------------------------
    # --- IFCONFIG COMMAND EXECUTION ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _run_ifconfig_command() -> str:
        """
        Run the `ifconfig` command and return its stdout.
        """
        try:
            return subprocess.check_output(
                NetworkInterfacesResolver._IFCONFIG_CMD,
                stderr=subprocess.STDOUT,
                text=True
            )
        except Exception:
            return ''

    # --------------------------------------------------------------------------
    # --- BASE DATA PARSERS ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _split_into_blocks(output: str) -> List[str]:
        """
        Split full `ifconfig` output into per-interface blocks.
        """
        blocks: List[str] = []
        current: List[str] = []

        for line in (output or '').splitlines():
            if line and not line.startswith('\t') and (':' in line.split()[0]):
                if current:
                    blocks.append('\n'.join(current))
                    current = []
            current.append(line.rstrip())

        if current:
            blocks.append('\n'.join(current))
        return blocks
    
    @classmethod
    def _parse_network_block(cls, block: str) -> Optional[InterfaceInfo]:
        """
        Parse a single interface block into an InterfaceInfo object.
        """
        if not block:
            return None

        # Create InterfaceInfo object with safe defaults.  # FIX: correct factory name
        info = cls._create_interface_info_model()

        # Create InterfaceStatistics objects with safe defaults.  # FIX: correct factory + enum
        rx_stats = cls._create_interface_statistics_model(InterfaceChannel.RX)
        tx_stats = cls._create_interface_statistics_model(InterfaceChannel.TX)

        # Iterate each line, classify, then delegate to a specific parser.
        for line in block.splitlines():
            kind = cls._classify_line(line)

            if kind == cls._HEADER_LINE:
                cls._parse_header_line(info, line)
            elif kind == cls._IPV4_LINE:
                cls._parse_ipv4_line(info, line)
            elif kind == cls._IPV6_LINE:
                cls._parse_ipv6_line(info, line)
            elif kind == cls._RX_LINE:
                cls._parse_rx_packets_line(rx_stats, line)
            elif kind == cls._TX_LINE:
                cls._parse_tx_packets_line(tx_stats, line)
            elif kind == cls._ERRORS_LINE:
                rx_stats, tx_stats = cls._parse_error_line(rx_stats, tx_stats, line)
            elif kind == cls._META_LINE:
                cls._parse_meta_line(info, line)
            else:
                continue

        info.statistics.append(rx_stats)
        info.statistics.append(tx_stats)

        # Return None if header was not parsed (no interface name)
        return info if info.network else None
    
    @classmethod
    def _parse_all_blocks(cls, raw: str) -> List[InterfaceInfo]:
        """
        Parse entire `ifconfig` output into a list of InterfaceInfo objects.
        """
        result: List[InterfaceInfo] = []
        for block in cls._split_into_blocks(raw):
            item = cls._parse_network_block(block)
            if item:
                result.append(item)
        return result
    
    # --------------------------------------------------------------------------
    # --- PUBLIC METHODS ---
    # --------------------------------------------------------------------------

    @classmethod
    def get_network_interfaces(cls) -> List[InterfaceInfo]:
        """
        Return parsed information for all network interfaces.
        """
        raw = cls._run_ifconfig_command()
        return cls._parse_all_blocks(raw)

    @classmethod
    def get_network_interface(cls, iface: str) -> Optional[InterfaceInfo]:
        """
        Return parsed information for a single interface by name.
        """
        for info in cls.get_network_interfaces():
            if info.network == iface:
                return info
        return None