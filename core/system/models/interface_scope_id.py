from __future__ import annotations

from core.data.enum_str import StrEnum


class InterfaceScopeId(StrEnum):
    COMPAT = 'COMPAT'
    GLOBAL = 'GLOBAL'
    HOST = 'HOST'
    LINK = 'LINK'
    NODE = 'NODE'
    ORG = 'ORG'
    SITE = 'SITE'
    UNKNOWN = 'UNKNOWN'

