from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Literal, Tuple


AccessLevel = Literal['User', 'Admin', 'Root']


@dataclass
class User:
    # Field-name constants (single source of truth for storage and APIs)
    FIELD_ID: ClassVar[str] = 'id'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_PASSWORD: ClassVar[str] = 'password'
    FIELD_PASSWORD_HASH: ClassVar[str] = 'password_hash'
    FIELD_LEVEL: ClassVar[str] = 'level'

    # --- Role constants (single source of truth for role names) ---
    LEVEL_USER: ClassVar[str] = "User"
    LEVEL_ADMIN: ClassVar[str] = "Admin"
    LEVEL_ROOT: ClassVar[str] = "Root"

    # Fields
    id: str
    name: str
    password_hash: str
    level: AccessLevel = 'User'

    def to_public(self) -> Dict[str, Any]:
        # Public shape returned to clients (no password hash)
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name,
            self.FIELD_LEVEL: self.level,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        # Full storage representation
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name,
            self.FIELD_PASSWORD_HASH: self.password_hash,
            self.FIELD_LEVEL: self.level,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'User':
        # Build model from storage dictionary using class-level field constants
        return cls(
            id=d[cls.FIELD_ID],
            name=d[cls.FIELD_NAME],
            password_hash=d[cls.FIELD_PASSWORD_HASH],
            level=d.get(cls.FIELD_LEVEL, 'User'),
        )
    
    @classmethod
    def get_levels(cls) -> Tuple[str]:
        return (
            cls.LEVEL_USER,
            cls.LEVEL_ADMIN,
            cls.LEVEL_ROOT
        )
    
    # region --- Optional helpers to build JSON Schemas for Swagger without magic strings ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ID: {'type': 'string', 'example': '550e8400-e29b-41d4-a716-446655440000'},
                cls.FIELD_NAME: {'type': 'string', 'example': 'alice'},
                cls.FIELD_LEVEL: {'type': 'string', 'enum': ['User', 'Admin', 'Root'], 'example': 'User'},
            },
            'required': [cls.FIELD_ID, cls.FIELD_NAME, cls.FIELD_LEVEL],
        }

    @classmethod
    def schema_add_request(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'minLength': 1, 'example': 'alice'},
                cls.FIELD_PASSWORD: {'type': 'string', 'minLength': 1, 'example': 'secret'},
                cls.FIELD_LEVEL: {'type': 'string', 'enum': ['User', 'Admin', 'Root'], 'default': 'User'},
            },
            'required': [cls.FIELD_NAME, 'password'],
        }

    @classmethod
    def schema_update_request(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'minLength': 1, 'example': 'alice2'},
                cls.FIELD_PASSWORD: {'type': 'string', 'minLength': 1, 'example': 'newsecret'},
                cls.FIELD_LEVEL: {'type': 'string', 'enum': ['User', 'Admin', 'Root']},
            },
        }

    # endregion
