from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from supervisor_service.models.process_action import ProcessAction


@dataclass
class ProcessActionResult:
    # --- Field-name constants (unified response) ---
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_ACTION: ClassVar[str] = 'action'
    FIELD_STATE: ClassVar[str] = 'state'
    FIELD_MESSAGE: ClassVar[str] = 'message'

    # --- Fields ---
    name: str
    action: ProcessAction
    state: bool
    message: str = ''

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ProcessActionResult':
        return cls(
            name=d[cls.FIELD_NAME],
            action=ProcessAction.from_str(d[cls.FIELD_ACTION]),
            state=bool(d[cls.FIELD_STATE]),
            message=str(d.get(cls.FIELD_MESSAGE, '') or ''),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_NAME: self.name,
            self.FIELD_ACTION: self.action.value,
            self.FIELD_STATE: self.state,
            self.FIELD_MESSAGE: self.message,
        }

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'example': 'worker'},
                cls.FIELD_ACTION: {'type': 'string', 'enum': ProcessAction.get_all_str(), 'example': ProcessAction.START.value},
                cls.FIELD_STATE: {'type': 'boolean', 'example': True},
                cls.FIELD_MESSAGE: {'type': 'string', 'example': 'Process started successfully'},
            },
            'required': [cls.FIELD_NAME, cls.FIELD_ACTION, cls.FIELD_STATE],
        }