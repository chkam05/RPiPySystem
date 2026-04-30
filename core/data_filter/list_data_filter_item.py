from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from .list_filter_condition import ListFilterCondition
from core.data.public_data_model import PublicDataModel


@dataclass
class ListDataFilterItem(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_FIELD: ClassVar[str] = 'field'
    FIELD_CONDITION: ClassVar[str] = 'condition'
    FIELD_VALUE: ClassVar[str] = 'value'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    field: str
    condition: ListFilterCondition
    value: Any = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ListDataFilterItem:
        return cls(
            field=str(d.get(cls.FIELD_FIELD, '')).strip(),
            condition=ListFilterCondition.from_value(d.get(cls.FIELD_CONDITION, ListFilterCondition.EQUAL.value)),
            value=d.get(cls.FIELD_VALUE),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_FIELD: self.field,
            self.FIELD_CONDITION: self.condition.value,
            self.FIELD_VALUE: self.value,
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_FIELD: {'type': 'string', 'example': 'user_name', 'description': 'Field used for filtering.'},
                cls.FIELD_CONDITION: {
                    'type': 'string',
                    'enum': ListFilterCondition.get_all_str(),
                    'example': ListFilterCondition.CONTAINS.value,
                    'description': 'Filter condition.',
                },
                cls.FIELD_VALUE: {'nullable': True, 'example': 'pi', 'description': 'Value compared with the selected field.'},
            },
            'required': [cls.FIELD_FIELD, cls.FIELD_CONDITION],
        }
