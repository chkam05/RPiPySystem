from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List


class DataRowSorter:

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    @staticmethod
    def sort_rows(rows: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
        if not fields:
            return rows

        return sorted(rows, key=lambda row: tuple(DataRowSorter._sort_value(row.get(field)) for field in fields))

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    @staticmethod
    def _sort_value(value: Any):
        if value is None:
            return (1, '')
        if isinstance(value, (int, float)):
            return (0, value)
        if isinstance(value, datetime):
            return (0, value.isoformat())

        return (0, str(value).casefold())
