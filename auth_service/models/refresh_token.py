from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Literal

from core.data.public_data_model import PublicDataModel


@dataclass
class RefreshToken(PublicDataModel):

    _TOKEN_TYPE: ClassVar[str] = 'refresh'

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_TYP: ClassVar[str] = 'typ'
    FIELD_JTI: ClassVar[str] = 'jti'
    FIELD_SUB: ClassVar[str] = 'sub'
    FIELD_IAT: ClassVar[str] = 'iat'
    FIELD_EXP: ClassVar[str] = 'exp'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    typ: Literal['refresh']     # Token type identifier
    jti: str                    # Token ID (UUID)
    sub: str                    # User ID (UUID)
    iat: int                    # Issued at timestamp (unix)
    exp: int                    # Expiration timestamp (unix)

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RefreshToken:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        if d.get(cls.FIELD_TYP) != cls._TOKEN_TYPE:
            raise ValueError('Invalid token type')
        
        return cls(
            typ=cls._TOKEN_TYPE,
            jti=str(d[cls.FIELD_JTI]),
            sub=str(d[cls.FIELD_SUB]),
            iat=int(d[cls.FIELD_IAT]),
            exp=int(d[cls.FIELD_EXP]),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_TYP: self.typ,
            self.FIELD_JTI: self.jti,
            self.FIELD_SUB: self.sub,
            self.FIELD_IAT: self.iat,
            self.FIELD_EXP: self.exp,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_TYP: {'type': 'string', 'enum': ['refresh'], 'example': 'refresh'},
                cls.FIELD_JTI: {'type': 'string', 'example': '0e9f2b7e-6b9a-4fb3-a6ac-1f5c3a6b2e91'},
                cls.FIELD_SUB: {'type': 'string', 'example': '550e8400-e29b-41d4-a716-446655440000'},
                cls.FIELD_IAT: {'type': 'integer', 'example': 1710000000},
                cls.FIELD_EXP: {'type': 'integer', 'example': 1710000900},
            },
            'required': [cls.FIELD_TYP, cls.FIELD_JTI, cls.FIELD_SUB, cls.FIELD_IAT, cls.FIELD_EXP],
        }
