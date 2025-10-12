import time
from typing import Any, ClassVar, Dict, Optional
import uuid

from flask import jsonify, request
from itsdangerous import URLSafeSerializer

from auth_service.models.access_token import AccessToken
from auth_service.models.refresh_token import RefreshToken
from auth_service.models.token_pair import TokenPair
from auth_service.models.user import User
from auth_service.storage.sessions_storage import SessionsStorage
from auth_service.storage.users_storage import UsersStorage
from auth_service.utils.auth_guard import AuthGuard
from utils.auto_swag import auto_swag, bad_request, ok, request_body_json, unauthorized
from utils.base_controller import BaseController
from utils.flask_api_service import FlaskApiService
from utils.security import SecurityUtils


class SessionsController(BaseController):
    _CONTROLLER_NAME: ClassVar[str] = 'auth_sessions'
    _CONTROLLER_PATH: ClassVar[str] = 'sessions'

    def __init__(
            self,
            url_prefix_base: str,
            auth_guard: AuthGuard,
            sessions_storage: SessionsStorage,
            users_storage: UsersStorage,
            *,
            service: Optional[FlaskApiService] = None) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        if not auth_guard:
            raise ValueError('auth_guard is required')
        if not sessions_storage:
            raise ValueError('sessions_storage is required')
        if not users_storage:
            raise ValueError('users_storage is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        self.auth_guard = auth_guard
        self.sessions_storage = sessions_storage
        self.users_storage = users_storage
        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, service=service)
    
    def register_routes(self) -> 'SessionsController':
        self.add_url_rule('/login', view_func=self.login, methods=['POST'])
        self.add_url_rule('/refresh', view_func=self.refresh, methods=['POST'])
        self.add_url_rule('/validate', view_func=self.validate, methods=['POST'])
        self.add_url_rule('/logout', view_func=self.logout, methods=['POST'])
        self.add_url_rule('/me', view_func=self.me, methods=['GET'])
        return self
    
    # --- Tokens Registration methods ---

    def _issue_tokens(self, user: User, *, prev_refresh_jti: Optional[str] = None) -> TokenPair:
        """
        Generates a new access and refresh token (refresh rotated and stored in SessionsStorage).
        """
        now = int(time.time())

        access_payload = AccessToken(
            typ='access',
            jti=str(uuid.uuid4()),
            sub=user.id,
            nam=user.name,
            lvl=user.level,
            iat=now,
            exp=now + self.auth_guard.ACCESS_TTL,
        ).to_dict()

        refresh_payload = RefreshToken(
            typ='refresh',
            jti=str(uuid.uuid4()),
            sub=user.id,
            iat=now,
            exp=now + self.auth_guard.REFRESH_TTL,
        ).to_dict()

        access_token = self.auth_guard.serializer.dumps(access_payload)
        refresh_token = self.auth_guard.serializer.dumps(refresh_payload)

        # Register/rotation, tokens refresh
        self.sessions_storage.rotate_refresh(prev_refresh_jti, refresh_payload['jti'], user.id, refresh_payload['exp'])

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='Bearer',
            expires_in=self.auth_guard.ACCESS_TTL,
            user=user,
        )

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['sessions'],
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
            401: unauthorized('Invalid credentials'),
            400: bad_request('Invalid payload')
        }
    )
    def login(self):
        data = request.get_json(silent=True) or {}
        name = data.get('name')
        password = data.get('password')

        if not isinstance(name, str) or not isinstance(password, str):
            return jsonify({'message': 'invalid payload'}), 400

        user = self.users_storage.verify_credentials(name, password)
        if not user:
            return jsonify({'message': 'invalid credentials'}), 401

        return jsonify(self._issue_tokens(user).to_public()), 200
    
    @auto_swag(
        tags=['sessions'],
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
            401: unauthorized('Invalid or expired refresh token'),
        }
    )
    def refresh(self):
        data = request.get_json(silent=True) or {}
        rtok = data.get('refresh_token')

        if not isinstance(rtok, str) or not rtok:
            return jsonify({'message': 'invalid payload'}), 400

        # Decode and verify refresh payload
        try:
            raw = self.auth_guard.load_refresh(rtok)
            payload = RefreshToken.from_dict(raw)
        except ValueError:
            return jsonify({'message': 'invalid or expired refresh token'}), 401

        uid, jti = payload.sub, payload.jti

        # Checking SessionsStorage (revoked/expired)
        if not self.sessions_storage.is_valid(jti, uid):
            return jsonify({'message': 'refresh token revoked or unknown'}), 401

        user = self.users_storage.get_by_id(uid)
        if not user:
            return jsonify({'message': 'user not found'}), 401

        out = self._issue_tokens(user, prev_refresh_jti=jti)
        return jsonify(out.to_public()), 200
    
    @auto_swag(
        tags=['sessions'],
        summary='Validate access token',
        description='Verifies the Bearer access token and returns its payload if valid.',
        responses={
            200: ok(
                {
                    'type': 'object',
                    'properties': {
                        'valid': {'type': 'boolean'},
                        'user': User.schema_public(),
                        'token': AccessToken.schema_public()
                    }
                }
            ),
            401: unauthorized('Invalid or expired token'),
        },
    )
    def validate(self):
        try:
            user, payload_model = self.auth_guard.require_auth()
        except PermissionError as e:
            return jsonify({'message': 'invalid or expired token'}), 401

        return jsonify({'valid': True, 'user': user.to_public(), 'token': payload_model.to_dict()}), 200
    
    @auto_swag(
        tags=['sessions'],
        summary='Logout – revoke tokens',
        description='Revokes the provided tokens (from body or Authorization header) and ends the session.',
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
            200: ok(
                {
                    'type': 'object',
                    'properties': {
                        'revoked': {'type': 'boolean'}
                    }
                }
            ),
            401: unauthorized('Invalid refresh token')}
    )
    def logout(self):
        # Prefer refresh_token from body and also allow Bearer (e.g. CLI clients)
        data = request.get_json(silent=True) or {}
        rtok = data.get('refresh_token') or SecurityUtils.read_bearer_from_request()
        
        if not isinstance(rtok, str) or not rtok:
            return jsonify({'message': 'missing refresh token'}), 400

        try:
            raw = self.auth_guard.load_refresh(rtok)
            payload = RefreshToken.from_dict(raw)
        except ValueError:
            return jsonify({'message': 'invalid or expired refresh token'}), 401

        # Idempotent - if already invalid, return success
        if not self.sessions_storage.is_valid(payload.jti, payload.sub):
            return jsonify({'revoked': True}), 200

        self.sessions_storage.revoke(payload.jti)
        return jsonify({'revoked': True}), 200
    
    @auto_swag(
        tags=['sessions'],
        summary='Me – current user',
        description='Returns the current authenticated user derived from the Bearer access token.',
        responses={
            200: ok(User.schema_public()),
            401: unauthorized('Invalid or missing token')
        },
    )
    def me(self):
        try:
            user, _ = self.auth_guard.require_auth()
        except PermissionError as e:
            return jsonify({'message': 'invalid or expired token'}), 401

        return jsonify(user.to_public()), 200