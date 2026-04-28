from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.error_response import ErrorResponse

from ...data.data_model import DataModel


@dataclass
class AuthCheckResult(DataModel):

    _ERROR_CODE_MAPPING = {
        401: 'unauthorized',
        403: 'forbidden',
        503: 'service unavailable',
        Any: 'unknown error'
    }

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_AUTHENTICATED: ClassVar[str] = 'authenticated'
    FIELD_ERROR_CODE: ClassVar[str] = 'error_code'
    FIELD_ERROR_MESSAGE: ClassVar[str] = 'error_message'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    authenticated: bool = False
    error_code: Optional[int] = None
    error_message: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> AuthCheckResult:
        """Deserializes data from a dictionary in "attribute:value" format to an object."""
        return cls(
            authenticated=d[cls.FIELD_AUTHENTICATED],
            error_code=d[cls.FIELD_ERROR_CODE],
            error_message=d[cls.FIELD_ERROR_MESSAGE]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object to a dictionary in the format "attribute:value"."""
        return {
            self.FIELD_AUTHENTICATED: self.authenticated,
            self.FIELD_ERROR_CODE: self.error_code,
            self.FIELD_ERROR_MESSAGE: self.error_message
        }
    
    def to_error_response(self) -> ErrorResponse:
        return ErrorResponse(
            self._ERROR_CODE_MAPPING[self.error_code],
            self.error_code,
            details=self.error_message
        )
