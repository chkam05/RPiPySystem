from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional


@dataclass
class ProcessInfo:
    # --- Field-name constants ---
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_STATE: ClassVar[str] = 'state'
    FIELD_PID: ClassVar[str] = 'pid'

    # --- Fields ---
    name: str
    state: str
    pid: Optional[int] = None  # Can be None (process not running)

    # --- Utilities ---

    @classmethod
    def _decode_pid(cls, raw_pid: Any) -> Optional[int]:
        pid: Optional[int] = None

        if raw_pid is None or raw_pid == '':
            pid = None
        elif isinstance(raw_pid, int):
            pid = raw_pid
        else:
            # Attempt to cast string/float to int; on error - None
            try:
                pid = int(raw_pid)
            except Exception:
                pid = None

        return pid

    # --- Packaging methods ---

    @classmethod
    def from_supervisor_dict(cls, d: Dict[str, Any]) -> 'ProcessInfo':
        base_name = str(d.get('name', '') or '').strip()
        group = str(d.get('group', '') or '').strip()
        full_name = f"{group}:{base_name}" if group else base_name

        return cls(
            name=full_name,
            state=str(d.get('statename') or d.get('state') or ''),  # prefer string statename
            pid=cls._decode_pid(d.get('pid')),
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ProcessInfo':
        name = d[cls.FIELD_NAME]
        state = d[cls.FIELD_STATE]

        pid: Optional[int] = cls._decode_pid(d.get(cls.FIELD_PID, None))

        return cls(
            name=name,
            state=state,
            pid=pid
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_NAME: self.name,
            self.FIELD_STATE: self.state,
            self.FIELD_PID: self.pid,
        }
    
    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()
    
    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, rows: List[Dict[str, Any]]) -> List['ProcessInfo']:
        return [cls.from_dict(r) for r in (rows or [])]

    @classmethod
    def list_from_supervisor(cls, rows: List[Dict[str, Any]]) -> List['ProcessInfo']:
        return [cls.from_supervisor_dict(r if isinstance(r, dict) else dict(r)) for r in (rows or [])]

    @staticmethod
    def list_to_public(items: List['ProcessInfo']) -> List[Dict[str, Any]]:
        return [i.to_public() for i in (items or [])]
    
    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_NAME: {'type': 'string', 'example': 'worker'},
                cls.FIELD_STATE: {'type': 'string', 'example': 'RUNNING'},
                cls.FIELD_PID: {'type': 'integer', 'nullable': True, 'example': 1234}
            }
        }

    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }