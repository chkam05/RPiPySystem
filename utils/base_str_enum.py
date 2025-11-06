from enum import Enum
from typing import List


class BaseStrEnum(str, Enum):
    """
    Base class for string-based Enums with common helper methods.
    """

    @classmethod
    def _missing_(cls, value):
        """
        Called when the given value does not match any enum member.
        """
        if isinstance(value, str):
            v = value.strip()
            v_fold = v.casefold()
            for m in cls:
                if m.value.casefold() == v_fold or m.name.casefold() == v_fold:
                    return m
        return None

    @classmethod
    def get_all(cls) -> List['BaseStrEnum']:
        """
        Return a list of all enum members.
        """
        return list(cls)
    
    @classmethod
    def get_all_str(cls) -> List[str]:
        """
        Return a list of all enum values as strings.
        """
        return [m.value for m in cls]
    
    @classmethod
    def from_str(cls, s: str) -> 'BaseStrEnum':
        """
        Return an enum member matching the given string (case-insensitive).
        """
        m = cls._missing_(s)
        if m is not None:
            return m
        
        try:
            return cls(s)
        except ValueError:
            raise ValueError(f'Invalid {cls.__name__}: {s!r}') from None

    def __str__(self) -> str:
        """
        Return the enum value as string.
        """
        return self.value