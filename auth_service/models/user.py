from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict


@dataclass
class User:
    # Field-name constants (single source of truth for storage and APIs)
    FIELD_ID: ClassVar[str] = 'id'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_PASSWORD_HASH: ClassVar[str] = 'password_hash'

    # Fields
    id: str
    name: str
    password_hash: str

    def to_public(self) -> Dict[str, Any]:
        # Public shape returned to clients (no password hash)
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name
        }
    
    def to_dict(self) -> Dict[str, Any]:
        # Full storage representation
        return {
            self.FIELD_ID: self.id,
            self.FIELD_NAME: self.name,
            self.FIELD_PASSWORD_HASH: self.password_hash,
        }
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'User':
        # Build model from storage dictionary using class-level field constants
        return cls(
            id=d[cls.FIELD_ID],
            name=d[cls.FIELD_NAME],
            password_hash=d[cls.FIELD_PASSWORD_HASH],
        )
    
    # --- Optional helpers to build JSON Schemas for Swagger without magic strings ---
    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ID: {'type': 'string', 'example': '550e8400-e29b-41d4-a716-446655440000'},
                cls.FIELD_NAME: {'type': 'string', 'example': 'alice'},
            },
            'required': [cls.FIELD_ID, cls.FIELD_NAME],
        }

    @classmethod
    def schema_add_request(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'minLength': 1, 'example': 'alice'},
                'password': {'type': 'string', 'minLength': 1, 'example': 'secret'},
            },
            'required': [cls.FIELD_NAME, 'password'],
        }

    @classmethod
    def schema_update_request(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'minLength': 1, 'example': 'alice2'},
                'password': {'type': 'string', 'minLength': 1, 'example': 'newsecret'},
            },
        }
