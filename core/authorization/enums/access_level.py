from core.data.enum_str import StrEnum


class AccessLevel(StrEnum):
    USER = 'user'
    ADMIN = 'admin'
    ROOT = 'root'