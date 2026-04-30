from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict

from core.data.public_data_model import PublicDataModel


@dataclass
class DisplayText(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_TEXT: ClassVar[str] = 'text'
    FIELD_X: ClassVar[str] = 'x'
    FIELD_Y: ClassVar[str] = 'y'
    FIELD_CLEAR: ClassVar[str] = 'clear'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    text: str
    x: int = 0
    y: int = 0
    clear: bool = True

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> DisplayText:
        return cls(
            text=str(d.get(cls.FIELD_TEXT, '')),
            x=int(d.get(cls.FIELD_X, 0)),
            y=int(d.get(cls.FIELD_Y, 0)),
            clear=bool(d.get(cls.FIELD_CLEAR, True)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_TEXT: self.text,
            self.FIELD_X: self.x,
            self.FIELD_Y: self.y,
            self.FIELD_CLEAR: self.clear,
        }
