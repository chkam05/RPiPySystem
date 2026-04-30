from __future__ import annotations
from typing import Any, Dict, List

from .data_row_filter import DataRowFilter
from .data_row_selector import DataRowSelector
from .data_row_sorter import DataRowSorter
from .list_data_filter_normalizer import ListDataFilterNormalizer
from .list_data_request import ListDataRequest


class ListDataFilter:

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    available_fields: list[str] = []
    default_fields: list[str] = []

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    @classmethod
    def filter_data(cls, rows: List[Dict[str, Any]], list_request: ListDataRequest) -> List[Dict[str, Any]]:
        fields = cls._normalize_fields(list_request.fields)
        sort_fields = cls._normalize_fields(list_request.sort, default_fields=[])
        filters = ListDataFilterNormalizer.normalize_filters_by_fields(list_request.filter, cls.available_fields)

        rows = DataRowFilter.filter_rows(rows, filters)
        rows = DataRowSorter.sort_rows(rows, sort_fields)
        return [DataRowSelector.select_fields(row, fields) for row in rows]

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    @classmethod
    def _normalize_fields(cls, fields: List[str], default_fields: List[str] | None = None) -> List[str]:
        default = cls.default_fields if default_fields is None else default_fields
        normalized: List[str] = []
        available = set(cls.available_fields)

        for field in fields or default:
            key = str(field).strip()
            if key in available and key not in normalized:
                normalized.append(key)

        return normalized or list(default)
