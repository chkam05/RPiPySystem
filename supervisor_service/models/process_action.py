from enum import Enum
from typing import List


class ProcessAction(str, Enum):
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'

    # --- Get methods ---

    @classmethod
    def get_all(cls) -> List['ProcessAction']:
        return list(cls)
    
    @classmethod
    def get_all_str(cls) -> List[str]:
        return [m.value for m in cls]
    
    @classmethod
    def from_str(cls, s: str) -> 'ProcessAction':
        try:
            return cls(s.lower())
        except Exception:
            raise ValueError(f'invalid process action: {s!r}')
    
    def __str__(self) -> str:
        return self.value