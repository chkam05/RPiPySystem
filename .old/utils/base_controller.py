from abc import ABC, abstractmethod
from typing import Optional
from flask import Blueprint

from utils.flask_api_service import FlaskApiService

class BaseController(Blueprint):
    
    def __init__(
            self,
            name: str,
            import_name: str,
            url_prefix: str,
            *,
            service: Optional[FlaskApiService] = None) -> None:
        # Prefix normalization
        if not url_prefix.startswith('/'):
            url_prefix = '/' + url_prefix

        self._service = service

        super().__init__(name, import_name, url_prefix=url_prefix)
        # Auto-register routes defined by subclasses
        # Subclass should override register_routes() and call add_url_rule(...)
        self.register_routes()
    
    @staticmethod
    def join_prefix(base: str, *parts: str) -> str:
        base = '/' + base.strip('/')
        rest = '/'.join(p.strip('/') for p in parts if p is not None)
        return base if not rest else f'{base}/{rest}'

    @abstractmethod
    def register_routes(self) -> 'BaseController':
        # Subclasses must override and return self
        raise NotImplementedError(f'{self.__class__.__name__}.register_routes() must be overridden')
