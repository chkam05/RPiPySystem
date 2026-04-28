from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from .access_token import AccessToken
from .user import User
from core.data.public_data_model import PublicDataModel


@dataclass
class ValidationResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_VALID: ClassVar[str] = 'valid'
    FIELD_USER: ClassVar[str] = 'user'
    FIELD_ACCESS_TOKEN: ClassVar[str] = 'access_token'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    valid: bool = False
    user: Optional[User] = None
    access_token: Optional[AccessToken] = None


    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ValidationResponse:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        user = d[cls.FIELD_USER]
        access_token = d[cls.FIELD_ACCESS_TOKEN]

        return cls(
            valid=d[cls.FIELD_VALID],
            user=User.from_dict(user),
            access_token=AccessToken.from_dict(access_token)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_VALID: self.valid,
            self.FIELD_USER: self.user.to_dict(),
            self.FIELD_ACCESS_TOKEN: self.access_token.to_dict()
        }
    
    def to_public(self) -> Dict[str, Any]:
        """Serializes an object to a dictionary in "attribute:value" format for public view."""
        return {
            self.FIELD_VALID: self.valid,
            self.FIELD_USER: self.user.to_public(),
            self.FIELD_ACCESS_TOKEN: self.access_token.to_public()
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_VALID: {'type': 'boolean', 'example': True},
                cls.FIELD_USER: User.schema_public(),
                cls.FIELD_ACCESS_TOKEN: AccessToken.schema_public()
            },
            'required': [cls.FIELD_VALID],
        }