from __future__ import annotations

from core.data.enum_str import StrEnum


class ListFilterCondition(StrEnum):
    EQUAL = 'equal'
    NOT_EQUAL = 'not_equal'
    GREATER = 'greater'
    GREATER_OR_EQUAL = 'greater_or_equal'
    LESS = 'less'
    LESS_OR_EQUAL = 'less_or_equal'
    CONTAINS = 'contains'
    NOT_CONTAINS = 'not_contains'
    STARTS_WITH = 'starts_with'
    ENDS_WITH = 'ends_with'
    IN = 'in'
    NOT_IN = 'not_in'
    IS_NULL = 'is_null'
    IS_NOT_NULL = 'is_not_null'

    @classmethod
    def from_value(cls, value: object) -> ListFilterCondition:
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            normalized = value.strip().casefold().replace('-', '_').replace(' ', '_')
            aliases = {
                'eq': cls.EQUAL,
                'equals': cls.EQUAL,
                'ne': cls.NOT_EQUAL,
                'not_equals': cls.NOT_EQUAL,
                'gt': cls.GREATER,
                'greater_than': cls.GREATER,
                'gte': cls.GREATER_OR_EQUAL,
                'greater_equal': cls.GREATER_OR_EQUAL,
                'lt': cls.LESS,
                'less_than': cls.LESS,
                'lte': cls.LESS_OR_EQUAL,
                'less_equal': cls.LESS_OR_EQUAL,
                'like': cls.CONTAINS,
                'not_like': cls.NOT_CONTAINS,
                'startswith': cls.STARTS_WITH,
                'starts': cls.STARTS_WITH,
                'endswith': cls.ENDS_WITH,
                'ends': cls.ENDS_WITH,
                'null': cls.IS_NULL,
                'not_null': cls.IS_NOT_NULL,
            }
            if normalized in aliases:
                return aliases[normalized]

        return cls.from_str(str(value))
