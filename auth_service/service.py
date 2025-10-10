from typing import ClassVar, Optional
from flask import Flask
from flasgger import Swagger
import logging

from utils.flask_api_service import FlaskApiService


class AuthService(FlaskApiService):

    def _configure_swagger(self):
        from .swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE

        return Swagger(self.service, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    def _register_controllers(self):
        from .controllers.health import HealthController
        from .controllers.users import UsersController
        from .controllers.sessions import SessionsController

        self._service.register_blueprint(HealthController())
        self._service.register_blueprint(UsersController())
        self._service.register_blueprint(SessionsController())
