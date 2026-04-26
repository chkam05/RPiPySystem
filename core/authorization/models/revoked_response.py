from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from .access_token import AccessToken
from .user import User
from core.data.public_data_model import PublicDataModel


@dataclass
class RevokedResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_REVOKED: ClassVar[str] = 'revoked'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    revoked: bool = True

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RevokedResponse:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            revoked=d[cls.FIELD_REVOKED]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_REVOKED: self.revoked
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_REVOKED: {'type': 'boolean', 'example': True}
            },
            'required': [cls.FIELD_REVOKED],
        }
    