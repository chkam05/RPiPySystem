from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List

from core.data.public_data_model import PublicDataModel


@dataclass
class ProcessListRequest(PublicDataModel):
    FIELD_FIELDS: ClassVar[str] = 'fields'
    FIELD_SORT: ClassVar[str] = 'sort'

    fields: List[str] = field(default_factory=lambda: ['process_id', 'process_name', 'user_name'])
    sort: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ProcessListRequest:
        return cls(
            fields=cls._to_str_list(d.get(cls.FIELD_FIELDS), ['process_id', 'process_name', 'user_name']),
            sort=cls._to_str_list(d.get(cls.FIELD_SORT), []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_FIELDS: self.fields,
            self.FIELD_SORT: self.sort,
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

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_FIELDS: {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['id', 'name', 'user'],
                    'description': 'Fields returned for each process. Aliases id, name and user are supported.',
                },
                cls.FIELD_SORT: {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['user', 'name', 'id'],
                    'description': 'Fields used for multi-level sorting in OrderBy/ThenBy order.',
                },
            },
            'required': [],
        }
