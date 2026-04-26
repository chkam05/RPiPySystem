from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, TypeVar


T = TypeVar('T', bound='DataModel')


class DataModel(ABC):

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> DataModel:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        raise NotImplementedError('The from_dict() method must be overridden in the derived class.')
    
    @classmethod
    def from_list_dicts(cls: Type[T], rows: List[Dict[str, Any]]) -> List[T]:
        """Deserializes data from a list of "attribute:value" format dictionaries to a list of objects."""
        return [cls.from_dict(r) for r in (rows or [])]

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        raise NotImplementedError('The to_dict() method must be overridden in the derived class.')
    
    @staticmethod
    def to_list_dicts(items: List[DataModel] | None) -> List[Dict[str, Any]]:
        """Serializes a list of objects to a dictionary list in "attribute:value" format."""
        return [i.to_dict() for i in (items or [])]