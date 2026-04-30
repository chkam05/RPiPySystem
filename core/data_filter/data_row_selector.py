from __future__ import annotations
from typing import Any, Dict, List


class DataRowSelector:

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    @staticmethod
    def select_fields(row: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        return {field: row.get(field) for field in fields}
