from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class LoginRequest(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_USERNAME: ClassVar[str] = 'username'
    FIELD_PASSWORD: ClassVar[str] = 'password'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    username: str
    password: str

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> LoginRequest:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            username=d[cls.FIELD_USERNAME],
            password=d[cls.FIELD_PASSWORD]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_USERNAME: self.username,
            self.FIELD_PASSWORD: self.password
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_USERNAME: {'type': 'string', 'minLength': 5, 'example': 'administrator'},
                cls.FIELD_PASSWORD: {'type': 'string', 'minLength': 8, 'example': 'secret'},
            },
            'required': [cls.FIELD_USERNAME, cls.FIELD_PASSWORD],
        }
