from flask import Flask
from flasgger import Swagger
import logging

from .config import BIND, PORT
from .controllers.processes import ProcessesController
from .swagger import SWAGGER_TEMPLATE, SWAGGER_CONFIG


# Initialize Flask app
app = Flask(__name__)

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logging.getLogger('werkzeug').setLevel(logging.INFO)

# Register blueprints
app.register_blueprint(ProcessesController())

# Initialize Swagger using the external configuration
swagger = Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

# Run the service
if __name__ == '__main__':
    app.run(host=BIND, port=PORT)
