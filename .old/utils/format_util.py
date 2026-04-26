from typing import Any, Dict, List, Optional


class FormatUtil:

    def __new__(cls, *args, **kwargs):
        """
        Prevent instantiation of this static utility class.
        """
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')
    
    # --------------------------------------------------------------------------
    # --- PUBLIC METHODS ---
    # --------------------------------------------------------------------------

    @classmethod
    def dict_without_nulls(
        cls,
        obj: Dict[str, Any],
        keep_null_fields: Optional[List[str]] = None,
        prev_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return a dict with None values removed recursively.
        """
        if obj is None:
            return None
        
        keep = set(s.strip('/') for s in (keep_null_fields or []))
        result: Dict[str, Any] = {}

        for key, value in obj.items():
            key_str = str(key)
            path = key_str if prev_path is None else f'{prev_path}/{key_str}'

            # Case: None value.
            if value is None:
                if path in keep:
                    result[key] = None
                continue

            # Case: dict.
            if isinstance(value, dict):
                nested = cls.dict_without_nulls(value, keep, path)
                result[key] = nested
                continue

            # Case: list.
            if isinstance(value, list):
                nested = cls.list_without_nulls(value, keep, path)
                result[key] = nested
                continue

            # Primitive.
            result[key] = value
        
        return result
    
    @classmethod
    def list_without_nulls(
        cls,
        obj: List[Any],
        keep_null_fields: Optional[List[str]] = None,
        prev_path: Optional[str] = None,
    ) -> List[Any]:
        """
        Return a list with None values removed recursively.
        """
        if obj is None:
            return None
        
        keep = set(s.strip('/') for s in (keep_null_fields or []))
        result: List[Any] = []

        for item in obj:
            # Direct None in list.
            if item is None:
                # list-level path: prev_path.
                if prev_path in keep:
                    result.append(None)
                continue

            # Nested dict.
            if isinstance(item, dict):
                nested = cls.dict_without_nulls(item, keep, prev_path)
                result.append(nested)
                continue

            # Nested list.
            if isinstance(item, list):
                nested = cls.list_without_nulls(item, keep, prev_path)
                result.append(nested)
                continue

            # Primitive.
            result.append(item)

        return result