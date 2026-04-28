from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class ErrorResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_MESSAGE: ClassVar[str] = 'message'
    FIELD_CODE: ClassVar[str] = 'code'
    FIELD_DATE_TIME: ClassVar[str] = 'date_time'
    FIELD_DETAILS: ClassVar[str] = 'details'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    message: str
    code: int
    date_time: datetime = field(default_factory=datetime.now)
    details: Optional[str] = None

    # --------------------------------------------------------------------------------
    # CONVERSION
    # --------------------------------------------------------------------------------

    @staticmethod
    def _datetime_from_str(value: Any) -> Optional[datetime]:
        if value is None or value == '':
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))

        raise TypeError('"date_time" must be a datetime, string or None.')

    @staticmethod
    def _datetime_to_str(value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None

        return value.isoformat()

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ErrorResponse:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        date_time = d.get(cls.FIELD_DATE_TIME)
        
        return cls(
            message=d[cls.FIELD_MESSAGE],
            code=d.get(cls.FIELD_CODE, 500),
            date_time=cls._datetime_from_str(date_time),
            details=d.get(cls.FIELD_DETAILS, None)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_MESSAGE: self.message,
            self.FIELD_CODE: self.code,
            self.FIELD_DATE_TIME: self._datetime_to_str(self.date_time),
            self.FIELD_DETAILS: self.details
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(
            cls,
            message: str = 'Invalid value',
            code: int = 422,
            details = 'Invalid value in field name. It should contain at least 8 characters.'
        ) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_MESSAGE: {'type': 'string', 'example': message},
                cls.FIELD_CODE: {'type': 'integer', 'example': code},
                cls.FIELD_DATE_TIME: {'type': 'string', 'example': cls._datetime_to_str(datetime.now())},
                cls.FIELD_DETAILS: {'type': 'string', 'example': details}
            },
            'required': [cls.FIELD_MESSAGE, cls.FIELD_CODE, cls.FIELD_DATE_TIME],
        }
