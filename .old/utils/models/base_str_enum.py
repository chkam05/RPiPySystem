from __future__ import annotations
from enum import Enum
from typing import List


class BaseStrEnum(str, Enum):
    """Base enum class for string-valued enums with case-insensitive lookups."""

    @classmethod
    def _missing_(cls, value):
        """Return a matching enum member using case-insensitive lookup."""
        if isinstance(value, str):
            v = value.strip()
            v_fold = v.casefold()
            for m in cls:
                if m.value.casefold() == v_fold or m.name.casefold() == v_fold:
                    return m
        return None
    
    def __str__(self) -> str:
        """Return the enum member value as a string."""
        return self.value

    @classmethod
    def get_all(cls) -> List[BaseStrEnum]:
        """Return a list of all enum members."""
        return list(cls)
    
    @classmethod
    def get_all_str(cls) -> List[str]:
        """Return a list of all enum member values as strings."""
        return [m.value for m in cls]
    
    @classmethod
    def from_str(cls, s: str) -> BaseStrEnum:
        """Convert a string to an enum member using strict or case-insensitive matching."""
        m = cls._missing_(s)
        if m is not None:
            return m
        
        try:
            return cls(s)
        except ValueError:
            raise ValueError(f'Invalid {cls.__name__}: {s!r}') from None