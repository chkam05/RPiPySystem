from utils.base_str_enum import BaseStrEnum


class InterfaceScopeId(BaseStrEnum):
    COMPAT = 'COMPAT'
    GLOBAL = 'GLOBAL'
    HOST = 'HOST'
    LINK = 'LINK'
    NODE = 'NODE'
    ORG = 'ORG'
    SITE = 'SITE'
    UNKNOWN = 'UNKNOWN'