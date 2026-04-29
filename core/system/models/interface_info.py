from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional

from core.data.public_data_model import PublicDataModel
from core.system.enums.interface_device import InterfaceDevice
from core.system.enums.interface_flag import InterfaceFlag
from core.system.models.interface_scope_id import InterfaceScopeId
from core.system.models.interface_statistics import InterfaceStatistics


@dataclass
class InterfaceInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_NETWORK: ClassVar[str] = 'network'
    FIELD_FLAGS: ClassVar[str] = 'flags'
    FIELD_FLAGS_BIN: ClassVar[str] = 'flags_bin'
    FIELD_MTU: ClassVar[str] = 'mtu'
    FIELD_DEVICE: ClassVar[str] = 'device'
    FIELD_STATISTICS: ClassVar[str] = 'statistics'
    FIELD_INET: ClassVar[str] = 'inet'
    FIELD_NETMASK: ClassVar[str] = 'netmask'
    FIELD_BROADCAST: ClassVar[str] = 'broadcast'
    FIELD_INET6: ClassVar[str] = 'inet6'
    FIELD_PREFIXLEN: ClassVar[str] = 'prefixlen'
    FIELD_SCOPEID: ClassVar[str] = 'scopeid'
    FIELD_SCOPEID_INT: ClassVar[str] = 'scopeid_int'
    FIELD_ETHER: ClassVar[str] = 'ether'
    FIELD_TXQUEUELEN: ClassVar[str] = 'txqueuelen'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    network: str
    flags: List[InterfaceFlag] = field(default_factory=list)
    flags_bin: int = 0
    mtu: int = 0
    device: InterfaceDevice = InterfaceDevice.UNSPEC
    statistics: List[InterfaceStatistics] = field(default_factory=list)
    inet: Optional[str] = None
    netmask: Optional[str] = None
    broadcast: Optional[str] = None
    inet6: Optional[str] = None
    prefixlen: Optional[int] = None
    scopeid: Optional[InterfaceScopeId] = None
    scopeid_int: Optional[int] = None
    ether: Optional[str] = None
    txqueuelen: Optional[int] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> InterfaceInfo:
        return cls(
            network=d[cls.FIELD_NETWORK],
            flags=[InterfaceFlag.from_str(f) for f in d.get(cls.FIELD_FLAGS, [])],
            flags_bin=d.get(cls.FIELD_FLAGS_BIN, 0),
            mtu=d.get(cls.FIELD_MTU, 0),
            device=InterfaceDevice.from_str(d.get(cls.FIELD_DEVICE, InterfaceDevice.UNSPEC.value)),
            statistics=InterfaceStatistics.from_dict_list(d.get(cls.FIELD_STATISTICS, [])),
            inet=d.get(cls.FIELD_INET),
            netmask=d.get(cls.FIELD_NETMASK),
            broadcast=d.get(cls.FIELD_BROADCAST),
            inet6=d.get(cls.FIELD_INET6),
            prefixlen=d.get(cls.FIELD_PREFIXLEN),
            scopeid=InterfaceScopeId.from_str(d[cls.FIELD_SCOPEID]) if d.get(cls.FIELD_SCOPEID) else None,
            scopeid_int=d.get(cls.FIELD_SCOPEID_INT),
            ether=d.get(cls.FIELD_ETHER),
            txqueuelen=d.get(cls.FIELD_TXQUEUELEN),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_NETWORK: self.network,
            self.FIELD_FLAGS: [f.value for f in self.flags],
            self.FIELD_FLAGS_BIN: self.flags_bin,
            self.FIELD_MTU: self.mtu,
            self.FIELD_DEVICE: self.device.value,
            self.FIELD_STATISTICS: InterfaceStatistics.to_dict_list(self.statistics),
            self.FIELD_INET: self.inet,
            self.FIELD_NETMASK: self.netmask,
            self.FIELD_BROADCAST: self.broadcast,
            self.FIELD_INET6: self.inet6,
            self.FIELD_PREFIXLEN: self.prefixlen,
            self.FIELD_SCOPEID: self.scopeid.value if self.scopeid else None,
            self.FIELD_SCOPEID_INT: self.scopeid_int,
            self.FIELD_ETHER: self.ether,
            self.FIELD_TXQUEUELEN: self.txqueuelen,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NETWORK: {'type': 'string', 'example': 'eth0', 'description': 'Network interface name.'},
                cls.FIELD_FLAGS: {'type': 'array', 'items': {'type': 'string', 'enum': InterfaceFlag.get_all_str()}, 'example': [InterfaceFlag.UP.value, InterfaceFlag.RUNNING.value], 'description': 'Interface status flags.'},
                cls.FIELD_FLAGS_BIN: {'type': 'integer', 'example': 0, 'description': 'Numeric flags value if available.'},
                cls.FIELD_MTU: {'type': 'integer', 'example': 1500, 'description': 'Maximum transmission unit.'},
                cls.FIELD_DEVICE: {'type': 'string', 'enum': InterfaceDevice.get_all_str(), 'example': InterfaceDevice.ETHERNET.value, 'description': 'Detected interface device type.'},
                cls.FIELD_STATISTICS: {
                    'type': 'array',
                    'items': InterfaceStatistics.schema_public(),
                    'example': [InterfaceStatistics.from_dict({'channel': 'RX', 'packets': 1024, 'bytes': 1048576}).to_dict()],
                    'description': 'Receive and transmit statistics.',
                },
                cls.FIELD_INET: {'type': 'string', 'nullable': True, 'example': '192.168.1.20', 'description': 'IPv4 address.'},
                cls.FIELD_NETMASK: {'type': 'string', 'nullable': True, 'example': '255.255.255.0', 'description': 'IPv4 netmask.'},
                cls.FIELD_BROADCAST: {'type': 'string', 'nullable': True, 'example': '192.168.1.255', 'description': 'IPv4 broadcast address.'},
                cls.FIELD_INET6: {'type': 'string', 'nullable': True, 'example': 'fe80::1', 'description': 'IPv6 address.'},
                cls.FIELD_PREFIXLEN: {'type': 'integer', 'nullable': True, 'example': 64, 'description': 'IPv6 prefix length.'},
                cls.FIELD_SCOPEID: {'type': 'string', 'nullable': True, 'enum': InterfaceScopeId.get_all_str(), 'example': InterfaceScopeId.LINK.value, 'description': 'IPv6 scope identifier.'},
                cls.FIELD_SCOPEID_INT: {'type': 'integer', 'nullable': True, 'example': 2, 'description': 'Numeric IPv6 scope identifier.'},
                cls.FIELD_ETHER: {'type': 'string', 'nullable': True, 'example': 'dc:a6:32:00:00:00', 'description': 'MAC address.'},
                cls.FIELD_TXQUEUELEN: {'type': 'integer', 'nullable': True, 'example': 1000, 'description': 'Transmit queue length if available.'},
            },
            'required': [cls.FIELD_NETWORK],
        }
