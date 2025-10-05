from flask import Flask
from flasgger import Swagger
from .config import BIND, PORT
from .controllers.network import net_bp
from .controllers.weather import weather_bp
from .controllers.health import health_bp
from .swagger import SWAGGER_CONFIG

# Initialize Flask app
app = Flask(__name__)

# Register blueprints
app.register_blueprint(net_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(health_bp)

# Initialize Swagger using the external configuration
swagger = Swagger(app, config=SWAGGER_CONFIG)

# Run the service
if __name__ == '__main__':
    app.run(host=BIND, port=PORT)
