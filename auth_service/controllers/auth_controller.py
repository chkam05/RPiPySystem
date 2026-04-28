from __future__ import annotations
from auth_service.models.login_request import LoginRequest
from auth_service.models.refresh_request import RefreshRequest
from flask import jsonify, request
from typing import ClassVar

from auth_service.models.access_token import AccessToken
from auth_service.models.refresh_token import RefreshToken
from auth_service.models.revoked_response import RevokedResponse
from auth_service.models.token_pair import TokenPair
from auth_service.models.user import User
from auth_service.models.validation_response import ValidationResponse
from auth_service.storage.session_storage import SessionStorage
from auth_service.storage.user_storage import UserStorage
from auth_service.utilities.auth_guard import AuthGuard
from core.api.auto_swag import auto_swag, bad_request, ok, request_body_json, unauthorized
from core.api.base_controller import BaseController
from core.api.flask_api_service import FlaskApiService
from core.authorization.bearer_reader import BearerReader
from core.data.error_response import ErrorResponse


class AuthController(BaseController):
    _CONTROLLER_NAME: ClassVar[str] = 'Auth'
    _CONTROLLER_PATH: ClassVar[str] = ''

    def __init__(
            self,
            service: FlaskApiService,
            auth_guard: AuthGuard,
            session_storage: SessionStorage,
            user_storage: UserStorage,
            url_prefix_base: str
        ) -> None:
        # Arguments validation
        if not auth_guard:
            raise ValueError('"auth_guard" component is required.')
        if not session_storage:
            raise ValueError('"session_storage" component is required.')
        if not user_storage:
            raise ValueError('"user_storage" component is required.')
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('"url_prefix_base" argument is required (e.g.: "/api").')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        self._auth_guard = auth_guard
        self._session_storage = session_storage
        self._user_storage = user_storage

        super().__init__(service, self._CONTROLLER_NAME, __name__, url_prefix)
    
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
        tags=[_CONTROLLER_NAME],
        summary='Login — Issue Access & Refresh Tokens (Bearer)',
        description='Authenticates with credentials and returns a Bearer access token and a refresh token.',
        security=[],    # Public
        request_body=request_body_json(LoginRequest.schema_public()),
        responses={
            200: ok(TokenPair.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            400: bad_request(ErrorResponse.schema_public('invalid payload', 400, 'Invalid username or password.'))
        }
    )
    def login(self):
        data = LoginRequest.from_dict(request.get_json(silent=True) or {})
        username = data.username
        password = data.password

        if not isinstance(username, str):
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing username.')), 400
        
        if not isinstance(password, str):
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing password.')), 400

        user = self._user_storage.verify_credentials(username, password)
        if not user:
            return jsonify(ErrorResponse('invalid credentials', 401, details='Invalid username or password.')), 401
        
        self._user_storage.update_last_login(user.id)

        return jsonify(self._auth_guard.issue_tokens(user).to_public()), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Refresh – rotate refresh token',
        description='Validates the refresh token, rotates it, and returns a new access token (and refresh token).',
        security=[],    # Public
        request_body=request_body_json(RefreshRequest.schema_public()),
        responses={
            200: ok(TokenPair.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            400: bad_request(ErrorResponse.schema_public('invalid payload', 400, 'Missing access or refresh token.'))
        }
    )
    def refresh(self):
        data = RefreshRequest.from_dict(request.get_json(silent=True) or {})
        rtok = data.refresh_token

        if not isinstance(rtok, str) or not rtok:
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing refresh token.')), 400

        # Decode and verify refresh payload
        try:
            raw = self._auth_guard.load_refresh(rtok)
            payload = RefreshToken.from_dict(raw)
        except ValueError:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401

        uid, jti = payload.sub, payload.jti

        # Checking SessionsStorage (revoked/expired)
        if not self._session_storage.is_valid(jti, uid):
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401

        user = self._user_storage.get_user_by_id(uid)
        if not user:
            return jsonify(ErrorResponse('unauthorized', 401, details='Token not associated with a user.')), 401

        out = self._auth_guard.issue_tokens(user, prev_refresh_jti=jti)
        return jsonify(out.to_public()), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Validate access token',
        description='Verifies the Bearer access token and returns its payload if valid.',
        responses={
            200: ok(ValidationResponse.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
        },
    )
    def validate(self):
        try:
            user, payload_model = self._auth_guard.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        return jsonify(ValidationResponse(True, user, payload_model)), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Logout – revoke tokens',
        description='Revokes a refresh token from the body, an access token from Authorization header, or both.',
        security=[],    # Public
        request_body=request_body_json(RefreshRequest.schema_public()),
        responses={
            200: ok(RevokedResponse.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.')),
            400: bad_request(ErrorResponse.schema_public('invalid payload', 400, 'Missing access and refresh token.'))
        }
    )
    def logout(self):
        data = RefreshRequest.from_dict(request.get_json(silent=True) or {})
        rtok = data.refresh_token
        atok = BearerReader.read_bearer_from_request()
        
        if rtok is not None and not isinstance(rtok, str):
            return jsonify(ErrorResponse('invalid payload', 400, details='Invalid refresh token.')), 400
        
        if not rtok and not atok:
            return jsonify(ErrorResponse('invalid payload', 400, details='Missing access and refresh token.')), 400
        
        if atok:
            try:
                raw = self._auth_guard.load_access(atok)
                access_payload = AccessToken.from_dict(raw)
            except ValueError:
                return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401
            
            if not self._session_storage.is_valid_access(access_payload.jti):
                return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

            refresh_record = self._session_storage.get_refresh_by_access_jti(access_payload.jti)
            if not refresh_record or not self._session_storage.is_valid(refresh_record.jti, refresh_record.uid):
                return jsonify(ErrorResponse('unauthorized', 401, details='Token pair not found or expired.')), 401

            self._auth_guard.revoke(
                refresh_jti=refresh_record.jti,
                access_jti=access_payload.jti,
                access_expires_at=access_payload.exp)
            return jsonify(RevokedResponse(True)), 200

        try:
            raw = self._auth_guard.load_refresh(rtok)
            refresh_payload = RefreshToken.from_dict(raw)
        except ValueError:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401
        
        if not self._session_storage.is_valid(refresh_payload.jti, refresh_payload.sub):
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired refresh token.')), 401

        refresh_record = self._session_storage.get_refresh(refresh_payload.jti)
        if not refresh_record:
            return jsonify(ErrorResponse('unauthorized', 401, details='Token pair not found or expired.')), 401

        self._auth_guard.revoke(
            refresh_jti=refresh_record.jti,
            access_jti=refresh_record.access_jti,
            access_expires_at=refresh_record.access_exp)
        return jsonify(RevokedResponse(True)), 200
    
    @auto_swag(
        tags=[_CONTROLLER_NAME],
        summary='Me – current user',
        description='Returns the current authenticated user derived from the Bearer access token.',
        responses={
            200: ok(User.schema_public()),
            401: unauthorized(ErrorResponse.schema_public('unauthorized', 401, 'Unauthorized.'))
        },
    )
    def me(self):
        try:
            user, _ = self._auth_guard.require_auth()
        except PermissionError as e:
            return jsonify(ErrorResponse('unauthorized', 401, details='Invalid or expired access token.')), 401

        return jsonify(user.to_public()), 200
