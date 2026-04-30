from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class IOResponse(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_OK: ClassVar[str] = 'ok'
    FIELD_DATA: ClassVar[str] = 'data'
    FIELD_ERROR: ClassVar[str] = 'error'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    ok: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> IOResponse:
        return cls(
            ok=bool(d.get(cls.FIELD_OK, False)),
            data=dict(d.get(cls.FIELD_DATA, {})),
            error=d.get(cls.FIELD_ERROR),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_OK: self.ok,
            self.FIELD_DATA: self.data,
            self.FIELD_ERROR: self.error,
        }
