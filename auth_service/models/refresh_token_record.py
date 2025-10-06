from dataclasses import dataclass, asdict
from typing import Any, ClassVar, Dict


@dataclass
class RefreshTokenRecord:
    # Field-name constants (single source of truth for storage and APIs)
    FIELD_JTI: ClassVar[str] = 'jti'
    FIELD_UID: ClassVar[str] = 'uid'
    FIELD_EXP: ClassVar[str] = 'exp'
    FIELD_REVOKED: ClassVar[str] = 'revoked'

    # Fields
    jti: str        # Token ID (UUID)
    uid: str        # User ID (UUID)
    exp: int        # Expiration time (unix timestamp)
    revoked: bool   # Has the token been invalidated?

    def to_dict(self) -> Dict[str, Any]:
        # Full storage representation
        return {
            self.FIELD_JTI: self.jti,
            self.FIELD_UID: self.uid,
            self.FIELD_EXP: self.exp,
            self.FIELD_REVOKED: self.revoked,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RefreshTokenRecord':
        # Build model from storage dictionary using class-level field constants
        return cls(
            jti=data[cls.FIELD_JTI],
            uid=data[cls.FIELD_UID],
            exp=int(data[cls.FIELD_EXP]),
            revoked=bool(data.get(cls.FIELD_REVOKED, False)),
        )
    
    # region --- Helper methods ---

    def is_valid(self, now: int) -> bool:
        # Returns True if the token is active (not revoked or expired).
        return not self.revoked and self.exp > now

    # endregion --- Helper methods ---
