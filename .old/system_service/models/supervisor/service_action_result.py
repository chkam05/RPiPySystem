from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from .service_action import ServiceAction
from utils.models.public_model import PublicModel


T = TypeVar('T', bound='ServiceActionResult')


@dataclass
class ServiceActionResult(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_ACTION: ClassVar[str] = 'action'
    FIELD_STATE: ClassVar[str] = 'state'
    FIELD_MESSAGE: ClassVar[str] = 'message'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    name: str
    action: ServiceAction
    state: bool
    message: str = ''

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> ServiceActionResult:
        return cls(
            name=d[cls.FIELD_NAME],
            action=ServiceAction.from_str(d[cls.FIELD_ACTION]),
            state=bool(d[cls.FIELD_STATE]),
            message=str(d.get(cls.FIELD_MESSAGE, '') or ''),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_NAME: self.name,
            self.FIELD_ACTION: str(self.action),
            self.FIELD_STATE: self.state,
            self.FIELD_MESSAGE: self.message,
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        service_actions = ServiceAction.get_all_str()

        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'example': 'worker'},
                cls.FIELD_ACTION: {'type': 'string', 'enum': service_actions, 'example': str(ServiceAction.START)},
                cls.FIELD_STATE: {'type': 'boolean', 'example': True},
                cls.FIELD_MESSAGE: {'type': 'string', 'example': 'Process started successfully'},
            },
            'required': [cls.FIELD_NAME, cls.FIELD_ACTION, cls.FIELD_STATE],
            'additionalProperties': False,
        }