from core.api.swagger_spec import SwaggerSpec

from .config import ROUTE, SWAGGER_DESCRIPTION, SWAGGER_TITLE


def _join_route(*parts: str) -> str:
    cleaned = [str(part).strip('/') for part in parts if str(part).strip('/')]
    return '/' + '/'.join(cleaned)


SPECS = [
    SwaggerSpec(
        endpoint='apispec_devices',
        route='apispec/devices.json',
        name='Devices',
        title='Bluetooth Devices API',
        controller_path='devices',
    ),
    SwaggerSpec(
        endpoint='apispec_connections',
        route='apispec/connections.json',
        name='Connections',
        title='Bluetooth Connections API',
        controller_path='connections',
    ),
]


SWAGGER_TEMPLATE = {
    'openapi': '3.0.3',
    'info': {
        'title': SWAGGER_TITLE,
        'version': '1.0.0',
        'description': SWAGGER_DESCRIPTION
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
    'specs': [spec.build_spec(ROUTE) for spec in SPECS],

    # Define where Swagger UI will be served
    'specs_route': _join_route(ROUTE, 'swagger') + '/',
    'static_url_path': _join_route(ROUTE, 'swagger_static'),

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
