from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Literal

from auth_service.models.user import User


@dataclass
class TokenPair:
    # --- Field-name constants ---
    FIELD_ACCESS_TOKEN: ClassVar[str] = 'access_token'
    FIELD_REFRESH_TOKEN: ClassVar[str] = 'refresh_token'
    FIELD_TOKEN_TYPE: ClassVar[str] = 'token_type'
    FIELD_EXPIRES_IN: ClassVar[str] = 'expires_in'
    FIELD_USER: ClassVar[str] = 'user'

    # --- Fields ---
    access_token: str
    refresh_token: str
    token_type: Literal['Bearer']
    expires_in: int
    user: User

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'TokenPair':
        return cls(
            access_token=d[cls.FIELD_ACCESS_TOKEN],
            refresh_token=d[cls.FIELD_REFRESH_TOKEN],
            token_type=d[cls.FIELD_TOKEN_TYPE],
            expires_in=d[cls.FIELD_EXPIRES_IN],
            user=User.from_dict(d[cls.FIELD_USER]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_ACCESS_TOKEN: self.access_token,
            self.FIELD_REFRESH_TOKEN: self.refresh_token,
            self.FIELD_TOKEN_TYPE: self.token_type,
            self.FIELD_EXPIRES_IN: self.expires_in,
            self.FIELD_USER: self.user.to_dict()
        }
    
    def to_public(self) -> Dict[str, Any]:
        return {
            self.FIELD_ACCESS_TOKEN: self.access_token,
            self.FIELD_REFRESH_TOKEN: self.refresh_token,
            self.FIELD_TOKEN_TYPE: self.token_type,
            self.FIELD_EXPIRES_IN: self.expires_in,
            self.FIELD_USER: self.user.to_public()
        }
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ACCESS_TOKEN: {'type': 'string', 'example': 'eyJ...'},
                cls.FIELD_REFRESH_TOKEN: {'type': 'string', 'example': 'eyJ...'},
                cls.FIELD_TOKEN_TYPE: {'type': 'string', 'example': 'Bearer'},
                cls.FIELD_EXPIRES_IN: {'type': 'integer', 'example': 900},
                cls.FIELD_USER: User.schema_public(),
            },
            'required': [
                cls.FIELD_ACCESS_TOKEN,
                cls.FIELD_REFRESH_TOKEN,
                cls.FIELD_TOKEN_TYPE,
                cls.FIELD_EXPIRES_IN,
                cls.FIELD_USER,
            ],
        }