from __future__ import annotations

from core.data.enum_str import StrEnum


class InterfaceFlag(StrEnum):
    ALLMULTI = 'ALLMULTI'
    AUTOMEDIA = 'AUTOMEDIA'
    BROADCAST = 'BROADCAST'
    DEBUG = 'DEBUG'
    DORMANT = 'DORMANT'
    DYNAMIC = 'DYNAMIC'
    ECHO = 'ECHO'
    LOOPBACK = 'LOOPBACK'
    LOWER_UP = 'LOWER_UP'
    MASTER = 'MASTER'
    MULTICAST = 'MULTICAST'
    NOARP = 'NOARP'
    NOCARRIER = 'NO-CARRIER'
    NOTRAILERS = 'NOTRAILERS'
    POINTOPOINT = 'POINTOPOINT'
    PORTSEL = 'PORTSEL'
    PROMISC = 'PROMISC'
    RUNNING = 'RUNNING'
    SLAVE = 'SLAVE'
    UP = 'UP'
