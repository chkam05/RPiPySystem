from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from functools import wraps
from flasgger import swag_from
from flask import request

JSONSchema = Dict[str, Any]
ResponseObject = Dict[str, Any]
Responses = Dict[Union[int, str], ResponseObject]
Parameters = List[Dict[str, Any]]


_ACCEPTABLE_BOOL_QUERY_VALUES: Dict[bool, Tuple[str]] = {
    True: ('true', '1', 'yes', 'y', 'on'),
    False: ('false', '0', 'no', 'n', 'off')
}
_BAD_REQUEST_BASE_SCHEMA: Dict[str, Any] = {
    'type': 'object',
    'properties': {
        'message': {'type': 'string'}
    }
}
_UNPROCESSABLE_ENTITY_BASE_SCHEMA: Dict[str, Any] = {
    'type': 'object',
    'properties': {
        'errors': {
            'type': 'array',
            'items': {'type': 'string'}
        }
    }
}


# ------------------------------------------------------------------------------
# --- CONTENT & RESPONSE HELPERS ---
# ------------------------------------------------------------------------------

def _json_content(schema: JSONSchema, example: Any = None) -> Dict[str, Any]:
    """Build OpenAPI JSON content definition with an optional example."""
    content: Dict[str, Any] = {'application/json': {'schema': schema}}
    if example is not None:
        content['application/json']['example'] = example
    return content

def response(
        description: str,
        schema: Optional[JSONSchema] = None,
        example: Any = None,
        content: Optional[Dict[str, Any]] = None
    ) -> ResponseObject:
    """Build a generic OpenAPI response object with optional schema and content."""
    obj: ResponseObject = {'description': description}
    if content is not None:
        obj['content'] = content
    elif schema is not None or example is not None:
        obj['content'] = _json_content(schema or {'type': 'object'}, example)
    return obj

# --- COMMON RESPONSE SHORTCUTS ---

def ok(schema: Optional[JSONSchema] = None, example: Any = None, description: str = 'OK') -> ResponseObject:
    """Build a 200 OK-style response object with optional schema and example."""
    return response(description, schema=schema, example=example)

def created(schema: Optional[JSONSchema] = None, example: Any = None, description: str = 'Created') -> ResponseObject:
    """Build a 201 Created-style response object with optional schema and example."""
    return response(description, schema=schema, example=example)

def no_content(description: str = 'No Content') -> ResponseObject:
    """Build a 204 No Content-style response object without a body."""
    return {'description': description}

def bad_request(description: str = 'Bad Request', schema: Optional[JSONSchema] = None) -> ResponseObject:
    """Build a 400 Bad Request response object with an optional error schema."""
    return response(description, schema=schema or _BAD_REQUEST_BASE_SCHEMA)

def unauthorized(description: str = 'Unauthorized') -> ResponseObject:
    """Build a 401 Unauthorized response object without a body."""
    return {'description': description}

def forbidden(description: str = 'Forbidden') -> ResponseObject:
    """Build a 403 Forbidden response object without a body."""
    return {'description': description}

def not_found(description: str = 'Not Found') -> ResponseObject:
    """Build a 404 Not Found response object without a body."""
    return {'description': description}

def conflict(description: str = 'Conflict') -> ResponseObject:
    """Build a 409 Conflict response object without a body."""
    return {'description': description}

def unprocessable_entity(description: str = 'Unprocessable Entity', schema: Optional[JSONSchema] = None) -> ResponseObject:
    """Build a 422 Unprocessable Entity response object with an errors schema."""
    return response(description, schema=schema or _UNPROCESSABLE_ENTITY_BASE_SCHEMA)

def internal_error(description: str = 'Internal Server Error') -> ResponseObject:
    """Build a 500 Internal Server Error response object without a body."""
    return {'description': description}

# ------------------------------------------------------------------------------
# --- REQUEST BODY & PARAMETER HELPERS ---
# ------------------------------------------------------------------------------

def request_body_json(schema: JSONSchema, example: Any = None, required: bool = True) -> Dict[str, Any]:
    """Build an OpenAPI requestBody object for a JSON payload."""
    rb: Dict[str, Any] = {'required': required, 'content': {'application/json': {'schema': schema}}}
    if example is not None:
        rb['content']['application/json']['example'] = example
    return rb

def qparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    """Create an OpenAPI query parameter definition."""
    return {
        'in': 'query',
        'name': name,
        'schema': schema,
        **({'description': description} if description else {})
    }

def pparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    """Create an OpenAPI path parameter definition."""
    return {
        'in': 'path',
        'name': name,
        'required': True,
        'schema': schema,
        **({'description': description} if description else {})
    }

def hparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    """Create an OpenAPI header parameter definition."""
    return {
        'in': 'header',
        'name': name,
        'schema': schema,
        **({'description': description} if description else {})
    }

def cparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    """Create an OpenAPI cookie parameter definition."""
    return {
        'in': 'cookie',
        'name': name,
        'schema': schema,
        **({'description': description} if description else {})
    }

def get_bool_query_arg(name: str, default: bool = False) -> bool:
    """Safely parse a boolean query argument from the current request."""
    val = request.args.get(name)
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    val = val.strip().lower()
    if val in _ACCEPTABLE_BOOL_QUERY_VALUES[True]:
        return True
    if val in _ACCEPTABLE_BOOL_QUERY_VALUES[False]:
        return False
    return default

# ------------------------------------------------------------------------------
# --- SCHEMA HELPERS ---
# ------------------------------------------------------------------------------

def object_schema(properties: Dict[str, JSONSchema], required: Optional[List[str]] = None) -> JSONSchema:
    """Build a JSON Schema object definition with optional required fields."""
    schema: JSONSchema = {'type': 'object', 'properties': properties}
    if required:
        schema['required'] = required
    return schema

def array_of(items_schema: JSONSchema) -> JSONSchema:
    """Build a JSON Schema array definition for the given item schema."""
    return {'type': 'array', 'items': items_schema}

# ------------------------------------------------------------------------------
# --- MAIN DECORATOR ---
# ------------------------------------------------------------------------------

def auto_swag(
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    parameters: Optional[Parameters] = None,
    request_body: Optional[Dict[str, Any]] = None,  # Full OpenAPI requestBody.
    responses: Optional[Responses] = None,
    security: Optional[List[Dict[str, List[str]]]] = None,
    operation_id: Optional[str] = None,
    deprecated: bool = False
) -> Callable:
    """Create a flasgger decorator from a minimal OpenAPI specification."""
    # Universal decorator that builds minimal OpenAPI dict and passes it to flasgger.
    spec: Dict[str, Any] = {}
    if summary: spec['summary'] = summary
    if description: spec['description'] = description
    if tags: spec['tags'] = tags
    if parameters: spec['parameters'] = parameters
    if request_body: spec['requestBody'] = request_body
    if security: spec['security'] = security
    if operation_id: spec['operationId'] = operation_id
    if deprecated: spec['deprecated'] = True
    if responses:
        spec['responses'] = {str(k): v for k, v in responses.items()}
    if 'responses' not in spec:
        spec['responses'] = {'200': {'description': 'OK'}}

    return swag_from(spec)

# ------------------------------------------------------------------------------
# --- BLUEPRINT-LEVEL DEFAULTS ---
# ------------------------------------------------------------------------------

def tag_defaults(*default_tags: str) -> Callable[..., Callable]:
    """Create an auto_swag wrapper that injects default tags into route specs."""
    # Factory that injects default tags to every call of auto_swag.
    def _decorator(**kwargs):
        """Apply auto_swag with merged default tags and explicit tags."""
        merged_tags = list(kwargs.pop('tags', []) or [])
        for t in default_tags:
            if t not in merged_tags:
                merged_tags.append(t)
        return auto_swag(tags=merged_tags, **kwargs)
    return _decorator