from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Literal

from auth_service.models.access_level import AccessLevel


@dataclass
class AccessToken:
    # --- Field-name constants ---
    FIELD_TYP: ClassVar[str] = 'typ'
    FIELD_JTI: ClassVar[str] = 'jti'
    FIELD_SUB: ClassVar[str] = 'sub'
    FIELD_NAM: ClassVar[str] = 'nam'
    FIELD_LVL: ClassVar[str] = 'lvl'
    FIELD_IAT: ClassVar[str] = 'iat'
    FIELD_EXP: ClassVar[str] = 'exp'

    _TOKEN_TYPE: ClassVar[str] = 'access'

    # --- Fields ---
    typ: Literal['access']  # Token type identifier
    jti: str                # Token ID (UUID)
    sub: str                # User ID (UUID)
    nam: str                # Username
    lvl: AccessLevel        # User access level ("User", "Admin", "Root")
    iat: int                # Issued at timestamp (unix)
    exp: int                # Expiration timestamp (unix)

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'AccessToken':
        if d.get(cls.FIELD_TYP) != cls._TOKEN_TYPE:
            raise ValueError('Invalid token type')
        
        lvl = AccessLevel.from_str(d.get(cls.FIELD_LVL))
        
        return cls(
            typ=cls._TOKEN_TYPE,
            jti=str(d[cls.FIELD_JTI]),
            sub=str(d[cls.FIELD_SUB]),
            nam=str(d[cls.FIELD_NAM]),
            lvl=lvl,
            iat=int(d[cls.FIELD_IAT]),
            exp=int(d[cls.FIELD_EXP]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_TYP: self.typ,
            self.FIELD_JTI: self.jti,
            self.FIELD_SUB: self.sub,
            self.FIELD_NAM: self.nam,
            self.FIELD_LVL: self.lvl.value,
            self.FIELD_IAT: self.iat,
            self.FIELD_EXP: self.exp,
        }
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_TYP: {'type': 'string', 'enum': ['access'], 'example': 'access'},
                cls.FIELD_JTI: {'type': 'string', 'example': '0e9f2b7e-6b9a-4fb3-a6ac-1f5c3a6b2e91'},
                cls.FIELD_SUB: {'type': 'string', 'example': '550e8400-e29b-41d4-a716-446655440000'},
                cls.FIELD_NAM: {'type': 'string', 'example': 'alice'},
                cls.FIELD_LVL: {'type': 'string', 'enum': AccessLevel.get_all_str(), 'example': AccessLevel.USER.value},
                cls.FIELD_IAT: {'type': 'integer', 'example': 1710000000},
                cls.FIELD_EXP: {'type': 'integer', 'example': 1710000900},
            },
            'required': [cls.FIELD_TYP, cls.FIELD_JTI, cls.FIELD_SUB, cls.FIELD_NAM, cls.FIELD_LVL, cls.FIELD_IAT, cls.FIELD_EXP],
        }