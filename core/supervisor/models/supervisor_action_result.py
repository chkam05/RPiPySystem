from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel
from core.supervisor.enums.supervisor_action import SupervisorAction


@dataclass
class SupervisorActionResult(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_ACTION: ClassVar[str] = 'action'
    FIELD_STATE: ClassVar[str] = 'state'
    FIELD_MESSAGE: ClassVar[str] = 'message'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    name: str
    action: SupervisorAction
    state: bool
    message: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> SupervisorActionResult:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            name=d[cls.FIELD_NAME],
            action=SupervisorAction.from_str(d[cls.FIELD_ACTION]),
            state=bool(d[cls.FIELD_STATE]),
            message=d.get(cls.FIELD_MESSAGE, None),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_NAME: self.name,
            self.FIELD_ACTION: str(self.action),
            self.FIELD_STATE: self.state,
            self.FIELD_MESSAGE: self.message,
        }
    
    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'example': 'worker'},
                cls.FIELD_ACTION: {'type': 'string', 'enum': SupervisorAction.get_all_str(), 'example': str(SupervisorAction.START)},
                cls.FIELD_STATE: {'type': 'boolean', 'example': True},
                cls.FIELD_MESSAGE: {'type': 'string', 'example': 'Process started successfully'},
            },
            'required': [],
        }
