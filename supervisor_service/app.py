from flask import Flask, jsonify, request
from flasgger import Swagger
from .config import BIND, PORT
from .process_manager import ProcessManager
from .swagger import SWAGGER_CONFIG

# Initialize Flask app
app = Flask(__name__)
pm = ProcessManager()

@app.get('/api/processes')
def get_processes():
    return jsonify(pm.list_processes())

@app.post('/api/processes/<name>/start')
def start_process(name: str):
    return jsonify(pm.start(name))

@app.post('/api/processes/<name>/stop')
def stop_process(name: str):
    return jsonify(pm.stop(name))

@app.post('/api/processes/<name>/restart')
def restart_process(name: str):
    return jsonify(pm.restart(name))

@app.post('/api/stop_all')
def stop_all():
    return jsonify(pm.stop_all())

# Initialize Swagger using the external configuration
swagger = Swagger(app, config=SWAGGER_CONFIG)

# Run the service
if __name__ == '__main__':
    app.run(host=BIND, port=PORT)
