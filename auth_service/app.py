from flask import Flask
from flasgger import Swagger
from .config import BIND, PORT, SECRET
from .controllers.health import HealthController
from .controllers.users import UserController
from .swagger import SWAGGER_CONFIG

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET

# Register blueprints
# app.register_blueprint(users_bp)
# app.register_blueprint(sessions_bp)
app.register_blueprint(HealthController())
app.register_blueprint(UserController())

# Initialize Swagger using the external configuration
swagger = Swagger(app, config=SWAGGER_CONFIG)

# Run the service
if __name__ == '__main__':
    app.run(host=BIND, port=PORT)
