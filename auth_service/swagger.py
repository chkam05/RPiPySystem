SERVICE_NAME = 'auth'
SWAGGER_CONFIG = {
    'openapi': '3.0.3',
    'swagger_ui': True,
    'headers': [],

    # Define where the JSON spec will be served
    'specs': [
        {
            'endpoint': 'apispec',
            'route': f'/api/{SERVICE_NAME}/apispec.json',   # Full path (must include the prefix)
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],

    # Define where Swagger UI will be served
    'specs_route': f'/api/{SERVICE_NAME}/apidocs/',
    'static_url_path': f'/api/{SERVICE_NAME}/flasgger_static',

    # UI meta
    'title': 'Auth Service API',
    'uiversion': 3,
}