from __future__ import annotations
from typing import Callable, List

from .list_data_filter_item import ListDataFilterItem


class ListDataFilterNormalizer:

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    @staticmethod
    def normalize_filters(
            filters: List[ListDataFilterItem],
            resolve_field: Callable[[str], str | None]
        ) -> List[ListDataFilterItem]:
        result: List[ListDataFilterItem] = []
        for item in filters:
            field = resolve_field(item.field)
            if not field:
                continue
            result.append(ListDataFilterItem(field=field, condition=item.condition, value=item.value))

        return result

    @staticmethod
    def normalize_filters_by_fields(
            filters: List[ListDataFilterItem],
            available_fields: List[str]
        ) -> List[ListDataFilterItem]:
        available = set(available_fields)
        return ListDataFilterNormalizer.normalize_filters(
            filters,
            lambda field: field.strip() if field.strip() in available else None,
        )
