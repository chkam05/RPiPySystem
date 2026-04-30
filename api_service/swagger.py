from .config import ROUTE, SWAGGER_DESCRIPTION, SWAGGER_TITLE
from core.api.swagger_spec import SwaggerSpec


def _join_route(*parts: str) -> str:
    cleaned = [str(part).strip('/') for part in parts if str(part).strip('/')]
    return '/' + '/'.join(cleaned)


SPECS = [
    SwaggerSpec(
        endpoint='apispec_main',
        route='apispec/main.json',
        name='Main',
        title='Main API',
        controller_path='health',
    ),
    SwaggerSpec(
        endpoint='apispec_network',
        route='apispec/network.json',
        name='Network',
        title='Network API',
        controller_path='network',
    ),
    SwaggerSpec(
        endpoint='apispec_supervisor',
        route='apispec/supervisor.json',
        name='Supervisor',
        title='Supervisor API',
        controller_path='supervisor',
    ),
    SwaggerSpec(
        endpoint='apispec_system',
        route='apispec/system.json',
        name='System',
        title='System API',
        controller_path='system',
    )
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
