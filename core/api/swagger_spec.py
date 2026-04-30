from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict


@dataclass
class SwaggerSpec:

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_ENDPOINT: ClassVar[str] = 'endpoint'
    FIELD_ROUTE: ClassVar[str] = 'route'
    FIELD_NAME: ClassVar[str] = 'name'
    FIELD_TITLE: ClassVar[str] = 'title'
    FIELD_RULE_FILTER: ClassVar[str] = 'rule_filter'
    FIELD_MODEL_FILTER: ClassVar[str] = 'model_filter'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    endpoint: str
    route: str
    name: str
    title: str
    controller_path: str    # For rule_filter
    model_filter: Callable[[Any], bool] = field(default_factory=lambda: lambda tag: True)

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    def build_spec(self, url_base: str) -> Dict[str, Any]:
        return {
            self.FIELD_ENDPOINT: self.endpoint,
            self.FIELD_ROUTE: self._join_route(url_base, self.route),
            self.FIELD_NAME: self.name,
            self.FIELD_TITLE: self.title,
            self.FIELD_RULE_FILTER: self._controller_rule_filter(url_base),
            self.FIELD_MODEL_FILTER: self.model_filter,
        }

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    @staticmethod
    def _join_route(*parts: str) -> str:
        cleaned = [str(part).strip('/') for part in parts if str(part).strip('/')]
        return '/' + '/'.join(cleaned)

    def _controller_rule_filter(self, url_base: str):
        prefix = self._join_route(url_base, self.controller_path)
        return lambda rule: rule.rule.startswith(prefix)
