from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List

from .list_data_filter_item import ListDataFilterItem
from core.data.public_data_model import PublicDataModel


@dataclass
class ListDataRequest(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_FIELDS: ClassVar[str] = 'fields'
    FIELD_SORT: ClassVar[str] = 'sort'
    FIELD_FILTER: ClassVar[str] = 'filter'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    fields: list[str] = field(default_factory=list)
    sort: list[str] = field(default_factory=list)
    filter: list[ListDataFilterItem] = field(default_factory=list)

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def default_fields(cls) -> List[str]:
        return []

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ListDataRequest:
        return cls(
            fields=cls._to_str_list(d.get(cls.FIELD_FIELDS), cls.default_fields()),
            sort=cls._to_str_list(d.get(cls.FIELD_SORT), []),
            filter=cls._to_filter_list(d.get(cls.FIELD_FILTER)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_FIELDS: self.fields,
            self.FIELD_SORT: self.sort,
            self.FIELD_FILTER: [item.to_dict() for item in self.filter],
        }

    @staticmethod
    def _to_str_list(value: Any, default: List[str]) -> List[str]:
        if value is None:
            return list(default)
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value]

        return list(default)

    @staticmethod
    def _to_filter_list(value: Any) -> List[ListDataFilterItem]:
        if value is None:
            return []
        items = value if isinstance(value, list) else [value]

        result: List[ListDataFilterItem] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            result.append(ListDataFilterItem.from_dict(item))

        return result

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_FIELDS: {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': cls.default_fields(),
                    'description': 'Fields returned for each row.',
                },
                cls.FIELD_SORT: {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': cls.default_fields(),
                    'description': 'Fields used for multi-level sorting in OrderBy/ThenBy order.',
                },
                cls.FIELD_FILTER: {
                    'type': 'array',
                    'items': ListDataFilterItem.schema_public(),
                    'description': 'Filters applied to rows before sorting and field selection.',
                },
            },
            'required': [],
        }
