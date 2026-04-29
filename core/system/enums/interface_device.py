from __future__ import annotations

from core.data.enum_str import StrEnum


class InterfaceDevice(StrEnum):
    BOND = 'BOND'
    BRIDGE = 'BRIDGE'
    ETHERNET = 'ETHERNET'
    GRE_TUNNEL = 'GRE TUNNEL'
    IPIP_TUNNEL = 'IPIP TUNNEL'
    LOCAL_LOOPBACK = 'LOCAL LOOPBACK'
    LOOPBACK = 'LOOPBACK'
    PPP = 'PPP'
    SIT_TUNNEL = 'SIT TUNNEL'
    SIX_LO_WPAN = '6LOWPAN'
    UNSPEC = 'UNSPEC'
    VLAN = 'VLAN'
    WI_FI_RADIOTAP = 'WI-FI (RADIOTAP)'
