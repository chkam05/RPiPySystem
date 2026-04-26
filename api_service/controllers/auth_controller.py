from __future__ import annotations
from core.authorization.models.revoked_response import RevokedResponse
from flask import jsonify, request
from typing import ClassVar

from core.api.auth_guard_controller import AuthGuardController
from core.api.auto_swag import auto_swag, bad_request, ok, request_body_json, unauthorized
from core.api.flask_api_service import FlaskApiService
from core.authorization.auth_guard import AuthGuard
from core.authorization.bearer_reader import BearerReader
from core.authorization.models.access_token import AccessToken
from core.authorization.models.refresh_token import RefreshToken
from core.authorization.models.token_pair import TokenPair
from core.authorization.models.user import User
from core.authorization.models.validation_response import ValidationResponse
from core.data.error_response import ErrorResponse


class AuthController(AuthGuardController):
    _CONTROLLER_NAME: ClassVar[str] = 'auth'
    _CONTROLLER_PATH: ClassVar[str] = 'auth'

    def __init__(
            self,
            service: FlaskApiService,
            auth_guard: AuthGuard,
            url_prefix_base: str) -> None:
        
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(
            service,
            auth_guard,
            self._CONTROLLER_NAME,
            __name__,
            url_prefix)
    
    def register_routes(self) -> AuthController:
        self.add_url_rule('/login', view_func=self.login, methods=['POST'])
        self.add_url_rule('/refresh', view_func=self.refresh, methods=['POST'])
        self.add_url_rule('/validate', view_func=self.validate, methods=['POST'])
        self.add_url_rule('/logout', view_func=self.logout, methods=['POST'])
        self.add_url_rule('/me', view_func=self.me, methods=['GET'])
        return self
    
    # --------------------------------------------------------------------------------
    # ENDPOINTS
    # --------------------------------------------------------------------------------

    @auto_swag(
        tags=['auth'],
        summary='Login — Issue Access & Refresh Tokens (Bearer)',
        description='Authenticates with credentials and returns a Bearer access token and a refresh token.',
        security=[],    # Public
        request_body=request_body_json(
            {
                'type': 'object',
                'properties': {'name': {'type': 'string'}, 'password': {'type': 'string'}},
                'required': ['name', 'password']
            }
        ),
        responses={
            200: ok(TokenPair.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            400: bad_request(ErrorResponse.schema_public('invalid payload', 400, 'Invalid username or password.'))
        }
    )
    def login(self):
        data = request.get_json(silent=True) or {}
        username = data.get('name')
        password = data.get('password')

        if not isinstance(username, str):
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing username.')), 400
        
        if not isinstance(password, str):
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing password.')), 400

        user = self.auth.verify_credentials(username, password)
        if not user:
            return jsonify(ErrorResponse('invalid credentials', 401, details='Invalid username or password.')), 401
        
        self.auth.update_last_login(user.id)

        return jsonify(self.auth.issue_tokens(user).to_public()), 200
    
    @auto_swag(
        tags=['auth'],
        summary='Refresh – rotate refresh token',
        description='Validates the refresh token, rotates it, and returns a new access token (and refresh token).',
        security=[],    # Public
        request_body=request_body_json(
            {
                'type': 'object',
                'properties': {'refresh_token': {'type': 'string'}},
                'required': ['refresh_token']
            }
        ),
        responses={
            200: ok(TokenPair.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            400: bad_request(ErrorResponse.schema_public('invalid payload', 400, 'Missing access or refresh token.'))
        }
    )
    def refresh(self):
        data = request.get_json(silent=True) or {}
        rtok = data.get('refresh_token')

        if not isinstance(rtok, str) or not rtok:
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing refresh token.')), 400

        # Decode and verify refresh payload
        try:
            raw = self.auth.load_refresh(rtok)
            payload = RefreshToken.from_dict(raw)
        except ValueError:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401

        uid, jti = payload.sub, payload.jti

        # Checking SessionsStorage (revoked/expired)
        if not self.auth.is_valid_refresh_token(jti, uid):
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401

        user = self.auth.user_storage.get_user_by_id(uid)
        if not user:
            return jsonify(ErrorResponse('unauthorized', 401, details='Token not associated with a user.')), 401

        out = self.auth.issue_tokens(user, prev_refresh_jti=jti)
        return jsonify(out.to_public()), 200
    
    @auto_swag(
        tags=['auth'],
        summary='Validate access token',
        description='Verifies the Bearer access token and returns its payload if valid.',
        responses={
            200: ok(ValidationResponse.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def validate(self):
        try:
            user, payload_model = self.auth.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        return jsonify(ValidationResponse(True, user, payload_model)), 200
    
    @auto_swag(
        tags=['auth'],
        summary='Logout – revoke tokens',
        description='Revokes a refresh token from the body, an access token from Authorization header, or both.',
        security=[],    # Public
        request_body=request_body_json(
            {
                'type': 'object',
                'properties': {
                    'refresh_token': {'type': 'string'}
                }
            },
            required=False
        ),
        responses={
            200: ok(RevokedResponse.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            400: bad_request(ErrorResponse.schema_public('invalid payload', 400, 'Missing access and refresh token.'))
        }
    )
    def logout(self):
        data = request.get_json(silent=True) or {}
        rtok = data.get('refresh_token')
        atok = BearerReader.read_bearer_from_request()
        
        if rtok is not None and not isinstance(rtok, str):
            return jsonify(ErrorResponse('invalid payload', 400, details='Invalid refresh token.')), 400
        
        if not rtok and not atok:
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing access and refresh token.')), 400
        
        if atok:
            try:
                raw = self.auth.load_access(atok)
                access_payload = AccessToken.from_dict(raw)
            except ValueError:
                return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401
            
            if not self.auth.is_valid_access_token(access_payload.jti):
                return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

            refresh_record = self.auth.session_storage.get_refresh_by_access_jti(access_payload.jti)
            if not refresh_record or not self.auth.is_valid_refresh_token(refresh_record.jti, refresh_record.uid):
                return jsonify(ErrorResponse('unauthorized', 401, details='Token pair not found or expired.')), 401

            self.auth.revoke(
                refresh_jti=refresh_record.jti,
                access_jti=access_payload.jti,
                access_expires_at=access_payload.exp)
            return jsonify(RevokedResponse(True)), 200

        try:
            raw = self.auth.load_refresh(rtok)
            refresh_payload = RefreshToken.from_dict(raw)
        except ValueError:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401
        
        if not self.auth.is_valid_refresh_token(refresh_payload.jti, refresh_payload.sub):
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401

        refresh_record = self.auth.session_storage.get_refresh(refresh_payload.jti)
        if not refresh_record:
            return jsonify(ErrorResponse('unauthorized', 401, details='Token pair not found or expired.')), 401

        self.auth.revoke(
            refresh_jti=refresh_record.jti,
            access_jti=refresh_record.access_jti,
            access_expires_at=refresh_record.access_exp)
        return jsonify(RevokedResponse(True)), 200
    
    @auto_swag(
        tags=['auth'],
        summary='Me – current user',
        description='Returns the current authenticated user derived from the Bearer access token.',
        responses={
            200: ok(User.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.'))
        },
    )
    def me(self):
        try:
            user, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        return jsonify(user.to_public()), 200
