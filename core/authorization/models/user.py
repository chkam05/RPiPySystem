from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from core.authorization.enums.access_level import AccessLevel
from core.data.public_data_model import PublicDataModel


@dataclass
class User(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_ID: ClassVar[str] = 'id'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_PASSWORD: ClassVar[str] = 'password'
    FIELD_PASSWORD_HASH: ClassVar[str] = 'password_hash'
    FIELD_LEVEL: ClassVar[str] = 'level'
    FIELD_LAST_LOGIN: ClassVar[str] = 'last_login'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    id: str
    name: str
    password_hash: str
    level: AccessLevel = AccessLevel.USER
    last_login: Optional[datetime] = None

    # --------------------------------------------------------------------------------
    # CONVERSION
    # --------------------------------------------------------------------------------

    @staticmethod
    def _datetime_from_str(value: Any) -> Optional[datetime]:
        if value is None or value == '':
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))

        raise TypeError('"last_login" must be a datetime, string or None.')

    @staticmethod
    def _datetime_to_str(value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None

        return value.isoformat()

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> User:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        last_login = d.get(cls.FIELD_LAST_LOGIN)
        level = d.get(cls.FIELD_LEVEL, AccessLevel.USER.value)
        
        return cls(
            id=d[cls.FIELD_ID],
            name=d[cls.FIELD_NAME],
            password_hash=d[cls.FIELD_PASSWORD_HASH],
            level=AccessLevel.from_str(level),
            last_login=cls._datetime_from_str(last_login)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name,
            self.FIELD_PASSWORD_HASH: self.password_hash,
            self.FIELD_LEVEL: self.level.value,
            self.FIELD_LAST_LOGIN: self._datetime_to_str(self.last_login)
        }
    
    def to_public(self) -> Dict[str, Any]:
        """Serializes an object to a dictionary in "attribute:value" format for public view."""
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name,
            self.FIELD_LEVEL: self.level.value,
            self.FIELD_LAST_LOGIN: self._datetime_to_str(self.last_login)
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ID: {'type': 'string', 'example': '550e8400-e29b-41d4-a716-446655440000'},
                cls.FIELD_NAME: {'type': 'string', 'example': 'administrator'},
                cls.FIELD_LEVEL: {'type': 'string', 'enum': AccessLevel.get_all_str(), 'example': AccessLevel.USER.value},
                cls.FIELD_LAST_LOGIN: {'type': 'string', 'example': 'yyyy-MM-ddTHH:mm:sszzz'}
            },
            'required': [cls.FIELD_ID, cls.FIELD_NAME, cls.FIELD_LEVEL],
        }
    
    @classmethod
    def schema_add_request(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'minLength': 1, 'example': 'administrator'},
                cls.FIELD_PASSWORD: {'type': 'string', 'minLength': 1, 'example': 'secret'},
                cls.FIELD_LEVEL: {'type': 'string', 'enum': AccessLevel.get_all_str(), 'default': AccessLevel.USER.value},
            },
            'required': [cls.FIELD_NAME, cls.FIELD_PASSWORD],
        }
    
    @classmethod
    def schema_update_request(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'minLength': 1, 'example': 'admin'},
                cls.FIELD_PASSWORD: {'type': 'string', 'minLength': 1, 'example': 'new_secret'},
                cls.FIELD_LEVEL: {'type': 'string', 'enum': AccessLevel.get_all_str()},
            },
        }
