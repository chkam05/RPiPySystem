from __future__ import annotations
from abc import abstractmethod
from typing import Optional
from flask import Blueprint
from utils.flask_api_service import FlaskApiService


class BaseController(Blueprint):
    """Base blueprint controller for registering routes in a Flask API service."""

    def __init__(
            self,
            service: FlaskApiService,
            name: str,
            import_name: str,
            url_prefix: str) -> None:
        """Initialize the controller blueprint and optionally attach a FlaskApiService."""
        # --- Input arguments validation ---
        if not name:
            raise ValueError('\"name\" argument is required (e.g.: my_service).')
        if not import_name:
            raise ValueError('\"import_name\" argument is required (it should be path to the file).')
        if not url_prefix:
            raise ValueError('\"url_prefix\" argument is required (e.g.: \"/\")')

        super().__init__(
            name,
            import_name,
            url_prefix=self._normalize_prefix(url_prefix)
        )
        
        # Attach service (required).
        self._service = service

        # Register routes inside the blueprint.
        self.register_routes()

        # Automatically add this controller to the Flask app.
        self._service.service.register_blueprint(self)
    
    # --------------------------------------------------------------------------
    # --- PROPERTIES ---
    # --------------------------------------------------------------------------

    @property
    def logger(self):
        """Return the logger from the attached FlaskApiService."""
        return self._service.logger

    @property
    def service(self) -> FlaskApiService:
        """Return the attached FlaskApiService instance."""
        return self._service
    
    # --------------------------------------------------------------------------
    # --- HELPER METHODS ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _normalize_prefix(url_prefix: str):
        """Normalize the URL prefix so that it always starts with a leading slash."""
        return f'/{url_prefix}' if not url_prefix.startswith('/') else url_prefix
    
    @staticmethod
    def join_prefix(base: str, *parts: str) -> str:
        """Join a base prefix and additional parts into a single URL path."""
        base = '/' + base.strip('/')
        rest = '/'.join(p.strip('/') for p in parts if p is not None)
        return base if not rest else f'{base}/{rest}'
    
    # --------------------------------------------------------------------------
    # --- CONFIGURATION METHODS ---
    # --------------------------------------------------------------------------

    @abstractmethod
    def register_routes(self) -> BaseController:
        """Register all routes for this controller on the blueprint."""
        return self