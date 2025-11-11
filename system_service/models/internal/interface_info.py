from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

from system_service.models.internal.interface_device import InterfaceDevice
from system_service.models.internal.interface_flag import InterfaceFlag
from system_service.models.internal.interface_scope_id import InterfaceScopeId
from system_service.models.internal.interface_statistics import InterfaceStatistics


@dataclass
class InterfaceInfo:
    # --- Field-name constants ---
    FIELD_NETWORK: ClassVar[str] = 'network'
    FIELD_FLAGS: ClassVar[str] = 'flags'
    FIELD_FLAGS_BIN: ClassVar[str] = 'flags_bin'
    FIELD_MTU: ClassVar[str] = 'mtu'
    FIELD_INET: ClassVar[str] = 'inet'
    FIELD_NETMASK: ClassVar[str] = 'netmask'
    FIELD_BROADCAST: ClassVar[str] = 'broadcast'
    FIELD_INET6: ClassVar[str] = 'inet6'
    FIELD_PREFIXLEN: ClassVar[str] = 'prefixlen'
    FIELD_SCOPEID: ClassVar[str] = 'scopeid'
    FIELD_SCOPEID_INT: ClassVar[str] = 'scopeid_int'
    FIELD_ETHER: ClassVar[str] = 'ether'
    FIELD_TXQUEUELEN: ClassVar[str] = 'txqueuelen'
    FIELD_DEVICE: ClassVar[str] = 'device'
    FIELD_STATISTICS: ClassVar[str] = 'statistics'

    # --- Fields ---
    network: str
    flags: List[InterfaceFlag]
    flags_bin: int
    mtu: int
    device: InterfaceDevice
    statistics: List[InterfaceStatistics]

    inet: Optional[str] = None
    netmask: Optional[str] = None
    broadcast: Optional[str] = None
    inet6: Optional[str] = None
    prefixlen: Optional[int] = None
    scopeid: Optional[InterfaceScopeId] = None
    scopeid_int: Optional[int] = None
    ether: Optional[str] = None
    txqueuelen: Optional[int] = None

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'InterfaceInfo':
        flags = d.get(cls.FIELD_FLAGS, [])
        scopeid = d.get(cls.FIELD_SCOPEID)
        device = d.get(cls.FIELD_DEVICE, InterfaceDevice.UNSPEC.value)
        statistics = d.get(cls.FIELD_STATISTICS, [])

        return cls(
            network=d[cls.FIELD_NETWORK],
            flags=[InterfaceFlag.from_str(f) for f in (flags or [])],
            flags_bin=d.get(cls.FIELD_FLAGS_BIN, 0),
            mtu=d.get(cls.FIELD_MTU, 1500),
            inet=d.get(cls.FIELD_INET),
            netmask=d.get(cls.FIELD_NETMASK),
            broadcast=d.get(cls.FIELD_BROADCAST),
            inet6=d.get(cls.FIELD_INET6),
            prefixlen=d.get(cls.FIELD_PREFIXLEN),
            scopeid=InterfaceScopeId.from_str(scopeid) if scopeid else None,
            scopeid_int=d.get(cls.FIELD_SCOPEID_INT),
            ether=d.get(cls.FIELD_ETHER),
            txqueuelen=d.get(cls.FIELD_TXQUEUELEN),
            device=InterfaceDevice.from_str(device),
            statistics=[InterfaceStatistics.from_dict(s) for s in (statistics or [])]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_NETWORK: self.network,
            self.FIELD_FLAGS: [str(f) for f in (self.flags or [])],
            self.FIELD_FLAGS_BIN: self.flags_bin,
            self.FIELD_MTU: self.mtu,
            self.FIELD_INET: self.inet,
            self.FIELD_NETMASK: self.netmask,
            self.FIELD_BROADCAST: self.broadcast,
            self.FIELD_INET6: self.inet6,
            self.FIELD_PREFIXLEN: self.prefixlen,
            self.FIELD_SCOPEID: str(self.scopeid) if self.scopeid is not None else None,
            self.FIELD_SCOPEID_INT: self.scopeid_int,
            self.FIELD_ETHER: self.ether,
            self.FIELD_TXQUEUELEN: self.txqueuelen,
            self.FIELD_DEVICE: str(self.device),
            self.FIELD_STATISTICS: [s.to_dict() for s in (self.statistics or [])]
        }
    
    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, rows: List[Dict[str, Any]]) -> List['InterfaceInfo']:
        return [cls.from_dict(r) for r in (rows or [])]

    @staticmethod
    def list_to_public(items: List['InterfaceInfo']) -> List[Dict[str, Any]]:
        return [i.to_public() for i in (items or [])]
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        flag_values = InterfaceFlag.get_all_str()
        device_values = InterfaceDevice.get_all_str()
        scope_values = InterfaceScopeId.get_all_str()
        stats_schema = InterfaceStatistics.schema_public_list()

        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NETWORK: {'type': 'string', 'example': 'wlan0'},
                cls.FIELD_FLAGS: {
                    'type': 'array',
                    'items': {'type': 'string', 'enum': flag_values},
                    'example': ['UP', 'BROADCAST', 'RUNNING', 'MULTICAST']
                },
                cls.FIELD_FLAGS_BIN: {'type': 'integer', 'example': 4163},
                cls.FIELD_MTU: {'type': 'integer', 'example': 1500},
                cls.FIELD_INET: {'type': 'string', 'example': '192.168.8.142'},
                cls.FIELD_NETMASK: {'type': 'string', 'example': '255.255.255.0'},
                cls.FIELD_BROADCAST: {'type': 'string', 'example': '192.168.8.255'},
                cls.FIELD_INET6: {'type': 'string', 'example': 'fe80::dec3:eea0:be4f:e7c3'},
                cls.FIELD_PREFIXLEN: {'type': 'integer', 'example': 64},
                cls.FIELD_SCOPEID: {'type': 'string', 'enum': scope_values, 'example': 'LINK'},
                cls.FIELD_SCOPEID_INT: {'type': 'integer', 'example': 32},
                cls.FIELD_ETHER: {'type': 'string', 'example': 'd8:3a:dd:fc:3f:0b'},
                cls.FIELD_TXQUEUELEN: {'type': 'integer', 'example': 1000},
                cls.FIELD_DEVICE: {'type': 'string', 'enum': device_values, 'example': 'ETHERNET'},
                cls.FIELD_STATISTICS: {
                    **stats_schema,
                    'example': [
                        {'channel': 'RX', 'packets': 60471, 'bytes': 11234805, 'errors': 0, 'dropped': 4, 'overruns': 0, 'frame': 0, 'carrier': 0, 'collisions': 0},
                        {'channel': 'TX', 'packets': 62377, 'bytes': 17131137, 'errors': 0, 'dropped': 0, 'overruns': 0, 'frame': 0, 'carrier': 0, 'collisions': 0}
                    ]
                },
            },
            'required': [
                cls.FIELD_NETWORK, cls.FIELD_FLAGS, cls.FIELD_FLAGS_BIN,
                cls.FIELD_MTU, cls.FIELD_DEVICE, cls.FIELD_STATISTICS
            ],
            'additionalProperties': False
        }

    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }