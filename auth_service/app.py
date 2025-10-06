from flask import Flask
from flasgger import Swagger
import logging

from .config import BIND, PORT, SECRET
from .controllers.health import HealthController
from .controllers.sessions import SessionsController
from .controllers.users import UsersController
from .swagger import SWAGGER_TEMPLATE, SWAGGER_CONFIG

# Initialize Flask app
app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logging.getLogger('werkzeug').setLevel(logging.INFO)

app.config['SECRET_KEY'] = SECRET

# Register blueprints
app.register_blueprint(HealthController())
app.register_blueprint(UsersController())
app.register_blueprint(SessionsController())

# Initialize Swagger using the external configuration
swagger = Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

# Run the service
if __name__ == '__main__':
    app.run(host=BIND, port=PORT)
