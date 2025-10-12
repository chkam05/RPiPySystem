from enum import Enum
from typing import List


class AccessLevel(str, Enum):
    USER = 'user'
    ADMIN = 'admin'
    ROOT = 'root'

    # --- Get methods ---

    @classmethod
    def get_all(cls) -> List['AccessLevel']:
        return list(cls)
    
    @classmethod
    def get_all_str(cls) -> List[str]:
        return [m.value for m in cls]
    
    @classmethod
    def from_str(cls, s: str) -> 'AccessLevel':
        try:
            return cls(s.lower())
        except Exception:
            raise ValueError(f'invalid access level: {s!r}')
    
    def __str__(self) -> str:
        return self.value