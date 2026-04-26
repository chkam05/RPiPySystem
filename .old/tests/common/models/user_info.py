from dataclasses import dataclass


@dataclass
class UserInfo:
    id: str
    level: str
    name: str