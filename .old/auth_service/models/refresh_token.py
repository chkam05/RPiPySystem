from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Literal


@dataclass
class RefreshToken:
    # --- Field-name constants ---
    FIELD_TYP: ClassVar[str] = 'typ'
    FIELD_JTI: ClassVar[str] = 'jti'
    FIELD_SUB: ClassVar[str] = 'sub'
    FIELD_IAT: ClassVar[str] = 'iat'
    FIELD_EXP: ClassVar[str] = 'exp'

    _TOKEN_TYPE: ClassVar[str] = 'refresh'

    # --- Fields ---
    typ: Literal['refresh']     # Token type identifier
    jti: str                    # Token ID (UUID)
    sub: str                    # User ID (UUID)
    iat: int                    # Issued at timestamp (unix)
    exp: int                    # Expiration timestamp (unix)

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RefreshToken':
        if data.get(cls.FIELD_TYP) != cls._TOKEN_TYPE:
            raise ValueError('Invalid token type')
        
        return cls(
            typ=cls._TOKEN_TYPE,
            jti=str(data[cls.FIELD_JTI]),
            sub=str(data[cls.FIELD_SUB]),
            iat=int(data[cls.FIELD_IAT]),
            exp=int(data[cls.FIELD_EXP]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_TYP: self.typ,
            self.FIELD_JTI: self.jti,
            self.FIELD_SUB: self.sub,
            self.FIELD_IAT: self.iat,
            self.FIELD_EXP: self.exp,
        }