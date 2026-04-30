from __future__ import annotations
from typing import Any, Dict, List

from .list_filter_condition import ListFilterCondition
from .list_data_filter_item import ListDataFilterItem


class DataRowFilter:

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    @staticmethod
    def filter_rows(rows: List[Dict[str, Any]], filters: List[ListDataFilterItem]) -> List[Dict[str, Any]]:
        if not filters:
            return rows

        return [row for row in rows if all(DataRowFilter._matches_filter(row, item) for item in filters)]

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    @staticmethod
    def _matches_filter(row: Dict[str, Any], item: ListDataFilterItem) -> bool:
        current = row.get(item.field)
        expected = item.value
        condition = item.condition

        if condition == ListFilterCondition.IS_NULL:
            return current is None
        if condition == ListFilterCondition.IS_NOT_NULL:
            return current is not None
        if condition == ListFilterCondition.EQUAL:
            return DataRowFilter._compare_values(current, expected) == 0
        if condition == ListFilterCondition.NOT_EQUAL:
            return DataRowFilter._compare_values(current, expected) != 0
        if condition == ListFilterCondition.GREATER:
            return DataRowFilter._compare_values(current, expected) > 0
        if condition == ListFilterCondition.GREATER_OR_EQUAL:
            return DataRowFilter._compare_values(current, expected) >= 0
        if condition == ListFilterCondition.LESS:
            return DataRowFilter._compare_values(current, expected) < 0
        if condition == ListFilterCondition.LESS_OR_EQUAL:
            return DataRowFilter._compare_values(current, expected) <= 0
        if condition == ListFilterCondition.CONTAINS:
            return str(expected).casefold() in str(current or '').casefold()
        if condition == ListFilterCondition.NOT_CONTAINS:
            return str(expected).casefold() not in str(current or '').casefold()
        if condition == ListFilterCondition.STARTS_WITH:
            return str(current or '').casefold().startswith(str(expected).casefold())
        if condition == ListFilterCondition.ENDS_WITH:
            return str(current or '').casefold().endswith(str(expected).casefold())
        if condition == ListFilterCondition.IN:
            return current in (expected if isinstance(expected, list) else [expected])
        if condition == ListFilterCondition.NOT_IN:
            return current not in (expected if isinstance(expected, list) else [expected])

        return True

    @staticmethod
    def _compare_values(current: Any, expected: Any) -> int:
        if current is None and expected is None:
            return 0
        if current is None:
            return -1
        if expected is None:
            return 1

        current_number = DataRowFilter._to_float(current)
        expected_number = DataRowFilter._to_float(expected)
        if current_number is not None and expected_number is not None:
            if current_number == expected_number:
                return 0
            return 1 if current_number > expected_number else -1

        current_text = str(current).casefold()
        expected_text = str(expected).casefold()
        if current_text == expected_text:
            return 0
        return 1 if current_text > expected_text else -1

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None

        return None
