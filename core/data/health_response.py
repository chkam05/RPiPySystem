from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from .public_data_model import PublicDataModel


@dataclass
class HealthResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------
    
    FIELD_STATUS: ClassVar[str] = 'status'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    status: str

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(self, status: str = 'ok'):
        self.status = status

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> HealthResponse:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            status=d[cls.FIELD_STATUS]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_STATUS: self.status
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------
    
    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        """Returns the public schema of the object data for Swagger."""
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_STATUS: {'type': 'string', 'example': 'ok'}
            },
            'required': [cls.FIELD_STATUS],
        }
