from __future__ import annotations
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from flasgger import swag_from
from flask import request

JSONSchema = Dict[str, Any]
ResponseObject = Dict[str, Any]
Responses = Dict[Union[int, str], ResponseObject]
Parameters = List[Dict[str, Any]]

# --------------------------------------------------------------------------------
# --- Content & Response Helpers ---
# --------------------------------------------------------------------------------

def _json_content(schema: JSONSchema, example: Any = None) -> Dict[str, Any]:
    # Build OpenAPI 'content' for application/json
    content: Dict[str, Any] = {'application/json': {'schema': schema}}
    if example is not None:
        content['application/json']['example'] = example
    return content

def response(description: str,
             schema: Optional[JSONSchema] = None,
             example: Any = None,
             content: Optional[Dict[str, Any]] = None) -> ResponseObject:
    # Build a single response object
    obj: ResponseObject = {'description': description}
    if content is not None:
        obj['content'] = content
    elif schema is not None or example is not None:
        obj['content'] = _json_content(schema or {'type': 'object'}, example)
    return obj

# Common response shortcuts
def ok(schema: Optional[JSONSchema] = None, example: Any = None, description: str = 'OK') -> ResponseObject:
    return response(description, schema=schema, example=example)

def created(schema: Optional[JSONSchema] = None, example: Any = None, description: str = 'Created') -> ResponseObject:
    return response(description, schema=schema, example=example)

def no_content(description: str = 'No Content') -> ResponseObject:
    return {'description': description}

def bad_request(description: str = 'Bad Request', schema: Optional[JSONSchema] = None) -> ResponseObject:
    return response(description, schema=schema or {'type': 'object', 'properties': {'message': {'type': 'string'}}})

def unauthorized(description: str = 'Unauthorized') -> ResponseObject:
    return {'description': description}

def forbidden(description: str = 'Forbidden') -> ResponseObject:
    return {'description': description}

def not_found(description: str = 'Not Found') -> ResponseObject:
    return {'description': description}

def conflict(description: str = 'Conflict') -> ResponseObject:
    return {'description': description}

def unprocessable_entity(description: str = 'Unprocessable Entity', schema: Optional[JSONSchema] = None) -> ResponseObject:
    return response(description, schema=schema or {'type': 'object', 'properties': {'errors': {'type': 'array', 'items': {'type': 'string'}}}})

def internal_error(description: str = 'Internal Server Error') -> ResponseObject:
    return {'description': description}

# --------------------------------------------------------------------------------
# --- Request Body & Parameter Helpers ---
# --------------------------------------------------------------------------------

def request_body_json(schema: JSONSchema, example: Any = None, required: bool = True) -> Dict[str, Any]:
    # Build OpenAPI 3 requestBody for JSON
    rb: Dict[str, Any] = {'required': required, 'content': {'application/json': {'schema': schema}}}
    if example is not None:
        rb['content']['application/json']['example'] = example
    return rb

def qparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    return {'in': 'query', 'name': name, 'schema': schema, **({'description': description} if description else {})}

def pparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    return {'in': 'path', 'name': name, 'required': True, 'schema': schema, **({'description': description} if description else {})}

def hparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    return {'in': 'header', 'name': name, 'schema': schema, **({'description': description} if description else {})}

def cparam(name: str, schema: JSONSchema, description: str = '') -> Dict[str, Any]:
    return {'in': 'cookie', 'name': name, 'schema': schema, **({'description': description} if description else {})}

def get_bool_query_arg(name: str, default: bool = False) -> bool:
    """Safely parse boolean query argument."""
    val = request.args.get(name)
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    val = val.strip().lower()
    if val in ('true', '1', 'yes', 'y', 'on'):
        return True
    if val in ('false', '0', 'no', 'n', 'off'):
        return False
    return default

# --------------------------------------------------------------------------------
# --- Schema Helpers ---
# --------------------------------------------------------------------------------

def object_schema(properties: Dict[str, JSONSchema], required: Optional[List[str]] = None) -> JSONSchema:
    schema: JSONSchema = {'type': 'object', 'properties': properties}
    if required:
        schema['required'] = required
    return schema

def array_of(items_schema: JSONSchema) -> JSONSchema:
    return {'type': 'array', 'items': items_schema}

# --------------------------------------------------------------------------------
# --- Main Decorator ---
# --------------------------------------------------------------------------------

def auto_swag(
    summary: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    parameters: Optional[Parameters] = None,
    request_body: Optional[Dict[str, Any]] = None,   # full OpenAPI requestBody
    responses: Optional[Responses] = None,
    security: Optional[List[Dict[str, List[str]]]] = None,
    operation_id: Optional[str] = None,
    deprecated: bool = False
) -> Callable:
    # Universal decorator that builds minimal OpenAPI dict and passes it to flasgger
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

# --------------------------------------------------------------------------------
# --- Blueprint-level Defaults ---
# --------------------------------------------------------------------------------

def tag_defaults(*default_tags: str) -> Callable[..., Callable]:
    # Factory that injects default tags to every call of auto_swag
    def _decorator(**kwargs):
        merged_tags = list(kwargs.pop('tags', []) or [])
        for t in default_tags:
            if t not in merged_tags:
                merged_tags.append(t)
        return auto_swag(tags=merged_tags, **kwargs)
    return _decorator