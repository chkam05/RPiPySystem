from flask import Flask
from flasgger import Swagger
from typing import Any, ClassVar, Mapping, Optional
import logging


class FlaskApiService:
    """
    Base class for Flask API services.
    """

    # --- Base logger configuration ---
    _LOGGER_LEVEL: ClassVar[int] = logging.INFO
    _LOGGER_FORMAT: ClassVar[str] = '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'

    def __init__(self, host: str, port: int, service_name: str):
        """
        Initializing API service.
        """
        self._host = host
        self._port = port
        self._name = service_name
        self._service = Flask(__name__)
        self._logger = logging.getLogger(service_name)

        self._configure_logger()
        self._register_controllers()
        self._swagger = self._configure_swagger()
    
    # region --- Properties ---

    @property
    def logger(self) -> logging.Logger:
        """
        Returns the logger instance assigned to this Flask service.
        """
        return self._logger

    @property
    def name(self) -> str:
        return self._name

    @property
    def service(self) -> Flask:
        """
        Returns an instance of the Flask application.
        """
        return self._service
    
    @property
    def swagger(self) -> Swagger:
        """
        Returns the Swagger instance used by Flask.
        """
        return self._swagger

    # --- Configuration methods ---
    
    def _configure_logger(self):
        """
        Configures the logger for a given Flask instance.
        """
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(self._LOGGER_FORMAT))
            self._logger.addHandler(handler)
            self._logger.setLevel(self._LOGGER_LEVEL)
            self._logger.propagate = False
        
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self._logger.info(f'Logger initialized for {self._service.name}')

    def _configure_swagger(self, *, template: Optional[dict] = None, config: Optional[dict] = None) -> Swagger:
        """
        Creates and returns a Swagger instance.
        Can be overridden in child classes to change configuration.
        """
        return Swagger(self._service, template=template, config=config)
    
    def _register_controllers(self):
        """
        Registers Flask controllers (blueprints).
        Must be overridden in descendant classes.
        """
        raise NotImplementedError('The _register_controllers() method must be overridden in the derived class.')

    # --- Interface methods ---

    def run(self):
        """
        Launches the Flask service.
        """
        self._logger.info(f"Starting service on {self._host}:{self._port} ...")
        self._service.run(self._host, self._port)