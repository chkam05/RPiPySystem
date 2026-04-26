from abc import ABC, abstractmethod
from typing import ClassVar, Optional
import logging

from flask import Flask
from flasgger import Swagger


class FlaskApiService(ABC):
    """Base service class for running a Flask API."""

    _LOGGER_LEVEL: ClassVar[int] = logging.INFO
    _LOGGER_FORMAT: ClassVar[str] = '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'

    def __init__(self, host: str, port: int, service_name: str, *, enable_swagger: bool = True):
        """Initialize the Flask API service"""
        self._host = host
        self._port = port
        self._name = service_name
        self._enable_swagger = enable_swagger

        self._service = Flask(__name__)
        self._logger = logging.getLogger(service_name)

        self._configure_logger()
        self._register_controllers()
        self._register_error_handlers()

        self._swagger = self._configure_swagger() if enable_swagger else None
    
    # --------------------------------------------------------------------------
    # --- PROPERTIES ---
    # --------------------------------------------------------------------------

    @property
    def logger(self) -> logging.Logger:
        """Return the logger instance used by this service."""
        return self._logger

    @property
    def name(self) -> str:
        """Return the name of this service."""
        return self._name

    @property
    def service(self) -> Flask:
        """Return the underlying Flask application instance."""
        return self._service
    
    @property
    def swagger(self) -> Swagger:
        """Return the Swagger documentation instance for this service."""
        return self._swagger
    
    # --------------------------------------------------------------------------
    # --- CONFIGURATION METHODS ---
    # --------------------------------------------------------------------------

    def _configure_logger(self):
        """Configure the logger for the service and related components."""
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(self._LOGGER_FORMAT))
            self._logger.addHandler(handler)
            self._logger.setLevel(self._LOGGER_LEVEL)
            self._logger.propagate = False
        
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self._logger.info(f'Logger initialized for {self._service.name}')
    
    def _configure_swagger(self, *, template: Optional[dict] = None, config: Optional[dict] = None) -> Swagger:
        """Create and configure the Swagger instance for this service."""
        return Swagger(self._service, template=template, config=config)
    
    @abstractmethod
    def _register_controllers(self):
        """Register all API controllers (routes) for this service."""
        raise NotImplementedError('The _register_controllers() method must be overridden in the derived class.')
    
    def _register_error_handlers(self) -> None:
        """Register global error handlers for this service."""
        pass

    # --------------------------------------------------------------------------
    # --- PUBLIC METHODS ---
    # --------------------------------------------------------------------------

    def run(self, **kwargs):
        """Start the Flask development server for this service."""
        self._logger.info(f"Starting service on {self._host}:{self._port} ...")
        self._service.run(self._host, self._port, **kwargs)