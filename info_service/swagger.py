SERVICE_NAME = 'info'
SWAGGER_CONFIG = {
    'openapi': '3.0.3',
    'swagger_ui': True,

    # Define where the JSON spec will be served
    'specs': [
        {
            'endpoint': 'apispec',
            'route': f'/api/{SERVICE_NAME}/apispec.json',   # Full path (must include the prefix)
            'rule_filter': lambda rule: rule.rule.startswith(f'/api/{SERVICE_NAME}/'),
            'model_filter': lambda tag: True,
        }
    ],

    # Define where Swagger UI will be served
    'specs_route': f'/api/{SERVICE_NAME}/apidocs/',
    'static_url_path': f'/api/{SERVICE_NAME}/flasgger_static',

    # UI meta
    'title': 'Info Service API',
    'uiversion': 3,
}