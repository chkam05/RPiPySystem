from abc import ABC, abstractmethod
from flask import Blueprint

class BaseController(Blueprint):
    def __init__(self, name: str, import_name: str, *, url_prefix: str = '/') -> None:
        super().__init__(name, import_name, url_prefix=url_prefix)
        # Auto-register routes defined by subclasses
        # Subclass should override register_routes() and call add_url_rule(...)
        self.register_routes()

    @abstractmethod
    def register_routes(self) -> 'BaseController':
        # Subclasses must override and return self
        raise NotImplementedError(f'{self.__class__.__name__}.register_routes() must be overridden')
