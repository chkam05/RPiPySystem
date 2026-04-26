from __future__ import annotations
from typing import Any, Dict, List
from utils.models.data_model import DataModel


class PublicModel(DataModel):

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    def to_public(self) -> Dict[str, Any]:
        """Serializes an object to a dictionary in "attribute:value" format for public view."""
        return self.to_dict()
    
    @staticmethod
    def to_public_list(items: List['PublicModel'] | None) -> List[Dict[str, Any]]:
        """Serializes a list of objects to a dictionary list in "attribute:value" format for public view."""
        return [i.to_public() for i in (items or [])]

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        """Returns the public schema of the object data for Swagger."""
        return {
            'type': 'object',
            'properties': {},
            'required': [],
            'additionalProperties': False
        }
    
    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        """Returns the public schema of the data object collection for Swagger."""
        return {
            'type': 'array',
            'items': cls.schema_public()
        }