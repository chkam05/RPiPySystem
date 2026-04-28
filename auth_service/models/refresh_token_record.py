from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class RefreshTokenRecord(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_JTI: ClassVar[str] = 'jti'
    FIELD_UID: ClassVar[str] = 'uid'
    FIELD_EXP: ClassVar[str] = 'exp'
    FIELD_REVOKED: ClassVar[str] = 'revoked'
    FIELD_ACCESS_JTI: ClassVar[str] = 'access_jti'
    FIELD_ACCESS_EXP: ClassVar[str] = 'access_exp'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    jti: str        # Token ID (UUID)
    uid: str        # User ID (UUID)
    exp: int        # Expiration time (unix timestamp)
    revoked: bool   # Has the token been invalidated?
    access_jti: Optional[str] = None
    access_exp: Optional[int] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RefreshTokenRecord:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            jti=d[cls.FIELD_JTI],
            uid=d[cls.FIELD_UID],
            exp=int(d[cls.FIELD_EXP]),
            revoked=bool(d.get(cls.FIELD_REVOKED, False)),
            access_jti=d.get(cls.FIELD_ACCESS_JTI),
            access_exp=int(d[cls.FIELD_ACCESS_EXP]) if d.get(cls.FIELD_ACCESS_EXP) is not None else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_JTI: self.jti,
            self.FIELD_UID: self.uid,
            self.FIELD_EXP: self.exp,
            self.FIELD_REVOKED: self.revoked,
            self.FIELD_ACCESS_JTI: self.access_jti,
            self.FIELD_ACCESS_EXP: self.access_exp,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_JTI: {'type': 'string', 'example': '0e9f2b7e-6b9a-4fb3-a6ac-1f5c3a6b2e91'},
                cls.FIELD_UID: {'type': 'string', 'example': '550e8400-e29b-41d4-a716-446655440000'},
                cls.FIELD_EXP: {'type': 'integer', 'example': 1710000900},
                cls.FIELD_REVOKED: {'type': 'boolean', 'example': False},
                cls.FIELD_ACCESS_JTI: {'type': 'string', 'example': '0e9f2b7e-6b9a-4fb3-a6ac-1f5c3a6b2e91'},
                cls.FIELD_ACCESS_EXP: {'type': 'integer', 'example': 1710000900}
            },
            'required': [cls.FIELD_JTI, cls.FIELD_UID, cls.FIELD_EXP, cls.FIELD_REVOKED],
        }
    
    # --------------------------------------------------------------------------------
    # UTILITIES
    # --------------------------------------------------------------------------------

    def is_valid(self, now: int) -> bool:
        return not self.revoked and self.exp > now
