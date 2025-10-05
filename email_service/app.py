from flask import Flask
from flasgger import Swagger
from .config import BIND, PORT
from .controllers.send import send_bp
from .controllers.health import health_bp
from .swagger import SWAGGER_CONFIG

# Initialize Flask app
app = Flask(__name__)

# Register blueprints
app.register_blueprint(send_bp)
app.register_blueprint(health_bp)

# Initialize Swagger using the external configuration
swagger = Swagger(app, config=SWAGGER_CONFIG)

# Run the service
if __name__ == '__main__':
    app.run(host=BIND, port=PORT)
