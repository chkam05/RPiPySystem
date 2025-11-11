from dataclasses import dataclass
from typing import Any, ClassVar, Dict


@dataclass
class ExternalNetworkInfo:
    # --- Field-name constants ---
    FIELD_ADDRESS: ClassVar[str] = 'address'

    # --- Fields ---
    address: str

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ExternalNetworkInfo':
        return cls(
            address=d[cls.FIELD_ADDRESS]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_ADDRESS: self.address
        }
    
    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Schema methods ---

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

    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }