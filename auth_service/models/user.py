from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from auth_service.models.access_level import AccessLevel


@dataclass
class User:
    # --- Field-name constants ---
    FIELD_ID: ClassVar[str] = 'id'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_PASSWORD: ClassVar[str] = 'password'
    FIELD_PASSWORD_HASH: ClassVar[str] = 'password_hash'
    FIELD_LEVEL: ClassVar[str] = 'level'

    # --- Fields ---
    id: str
    name: str
    password_hash: str
    level: AccessLevel = AccessLevel.USER

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'User':
        level = AccessLevel.from_str(d.get(cls.FIELD_LEVEL, AccessLevel.USER.value))

        return cls(
            id=d[cls.FIELD_ID],
            name=d[cls.FIELD_NAME],
            password_hash=d[cls.FIELD_PASSWORD_HASH],
            level=level,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name,
            self.FIELD_PASSWORD_HASH: self.password_hash,
            self.FIELD_LEVEL: self.level.value,
        }
    
    def to_public(self) -> Dict[str, Any]:
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name,
            self.FIELD_LEVEL: self.level.value,
        }

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ID: {'type': 'string', 'example': '550e8400-e29b-41d4-a716-446655440000'},
                cls.FIELD_NAME: {'type': 'string', 'example': 'alice'},
                cls.FIELD_LEVEL: {'type': 'string', 'enum': AccessLevel.get_all_str(), 'example': AccessLevel.USER.value},
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
                cls.FIELD_LEVEL: {'type': 'string', 'enum': AccessLevel.get_all_str(), 'default': AccessLevel.USER.value},
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
                cls.FIELD_LEVEL: {'type': 'string', 'enum': AccessLevel.get_all_str()},
            },
        }