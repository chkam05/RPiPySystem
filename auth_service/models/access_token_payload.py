from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Literal

from auth_service.models.user import AccessLevel


@dataclass
@dataclass
class AccessTokenPayload:
    # Field-name constants (single source of truth)
    FIELD_TYP: ClassVar[str] = "typ"
    FIELD_JTI: ClassVar[str] = "jti"
    FIELD_SUB: ClassVar[str] = "sub"
    FIELD_NAM: ClassVar[str] = "nam"
    FIELD_LVL: ClassVar[str] = "lvl"
    FIELD_IAT: ClassVar[str] = "iat"
    FIELD_EXP: ClassVar[str] = "exp"

    # Fields
    typ: Literal["access"]  # Token type identifier
    jti: str                # Token ID (UUID)
    sub: str                # User ID (UUID)
    nam: str                # Username
    lvl: AccessLevel        # User access level ("User", "Admin", "Root")
    iat: int                # Issued at timestamp (unix)
    exp: int                # Expiration timestamp (unix)

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_TYP: self.typ,
            self.FIELD_JTI: self.jti,
            self.FIELD_SUB: self.sub,
            self.FIELD_NAM: self.nam,
            self.FIELD_LVL: self.lvl,
            self.FIELD_IAT: self.iat,
            self.FIELD_EXP: self.exp,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AccessTokenPayload":
        if d.get(cls.FIELD_TYP) != "access":
            raise ValueError("invalid token type")
        
        return cls(
            typ="access",
            jti=str(d[cls.FIELD_JTI]),
            sub=str(d[cls.FIELD_SUB]),
            nam=str(d[cls.FIELD_NAM]),
            lvl=d[cls.FIELD_LVL],
            iat=int(d[cls.FIELD_IAT]),
            exp=int(d[cls.FIELD_EXP]),
        )
