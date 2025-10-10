from typing import ClassVar, Optional
from flask import Flask
from flasgger import Swagger
import logging

from .controllers.health import HealthController
from .controllers.users import UsersController
from .controllers.sessions import SessionsController
from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE


class AuthService:
    _LOGGER_NAME: ClassVar[str] = 'werkzeug'
    _LOGGER_LEVEL: ClassVar[int] = logging.INFO
    _LOGGER_FORMAT: ClassVar[str] = '[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'

    def __init__(self, host: str, port: int, secret: Optional[str] = None):
        self._host = host
        self._port = port
        self._service = Flask(__name__)

        if secret and secret.strip():
            self._service.config['SECRET_KEY'] = secret

        self._configure_logger()
        self._register_controllers()
        self._swagger = Swagger(self.service, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

    # region --- Configuration ---

    @classmethod
    def _configure_logger(cls):
        logging.basicConfig(level=cls._LOGGER_LEVEL, format=cls._LOGGER_FORMAT)
        logging.getLogger(cls._LOGGER_NAME).setLevel(cls._LOGGER_LEVEL)
    
    def _register_controllers(self):
        self._service.register_blueprint(HealthController())
        self._service.register_blueprint(UsersController())
        self._service.register_blueprint(SessionsController())
    
    # endregion --- Configuration ---

    def run(self):
        self._service.run(self._host, self._port)
    