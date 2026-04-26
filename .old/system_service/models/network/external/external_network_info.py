from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='ExternalNetworkInfo')


@dataclass
class ExternalNetworkInfo(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_ADDRESS: ClassVar[str] = 'address'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    address: str

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> ExternalNetworkInfo:
        return cls(
            address=d[cls.FIELD_ADDRESS]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_ADDRESS: self.address
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_ADDRESS: {'type': 'string', 'example': '89.74.35.138'}
            },
            'required': [
                cls.FIELD_ADDRESS
            ],
            'additionalProperties': False
        }