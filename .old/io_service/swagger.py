SERVICE_NAME = 'io'
SWAGGER_TITLE = 'IO Service API'

SWAGGER_TEMPLATE = {
    'openapi': '3.0.3',
    'info': {
        'title': SWAGGER_TITLE,
        'version': '1.0.0',
        'description': (
            'Raspberry PI GPIO port management service.\n'
        )
    },
    'components': {
        'securitySchemes': {
            # Bearer token definition for Authorization header
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',  # UI shows a token input field
                'description': 'Enter your access token without the \'Bearer \' prefix.'
            }
        }
    },
    # Global rule — all endpoints require BearerAuth,
    # individual endpoints (e.g., /login) can override it with `security: []`
    'security': [{'BearerAuth': []}],
}

SWAGGER_CONFIG = {
    'openapi': '3.0.3',
    'swagger_ui': True,
    'headers': [],

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
    'title': SWAGGER_TITLE,
    'uiversion': 3,

    'config': {
        # Remember entered authorization across refreshes
        'persistAuthorization': True,
        # Optional: collapse models for clarity
        'docExpansion': 'none'
    },
}