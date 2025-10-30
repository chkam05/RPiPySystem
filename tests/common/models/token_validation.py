from dataclasses import dataclass
from typing import Optional

from tests.common.models.user_info import UserInfo


@dataclass
class TokenClaims:
    exp: int
    iat: int
    jti: str
    lvl: str
    nam: str
    sub: str
    typ: str


@dataclass
class TokenValidation:
    valid: bool
    token: Optional[TokenClaims]
    user: Optional[UserInfo]