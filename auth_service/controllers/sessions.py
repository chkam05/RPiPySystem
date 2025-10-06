import time
import uuid
from typing import Any, Dict, Optional
from flask import request, jsonify
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from utils.auto_swag import auto_swag, ok, bad_request, unauthorized, request_body_json
from utils.base_controller import BaseController

from auth_service.models.user import User
from auth_service.models.access_token_payload import AccessTokenPayload
from auth_service.models.refresh_token_payload import RefreshTokenPayload
from auth_service.storage.users_storage import UsersStorage
from auth_service.storage.sessions_storage import SessionsStorage
from auth_service.utils.auth_guard import AuthGuard
from auth_service import config


class SessionsController(BaseController):
    def __init__(
            self,
            *,
            url_prefix: str = "/api/auth/session",
            users: Optional[UsersStorage] = None,
            sessions: Optional[SessionsStorage] = None) -> None:
        self.users = users or UsersStorage()
        self.sessions = sessions or SessionsStorage()
        self.auth = AuthGuard(self.users)  # <— wspólna obsługa access tokenów
        self.serializer = URLSafeTimedSerializer(config.SECRET, salt="auth-tokens")
        self.ACCESS_TTL = getattr(config, "ACCESS_TOKEN_SECONDS", 15 * 60)
        self.REFRESH_TTL = getattr(config, "REFRESH_TOKEN_SECONDS", 30 * 24 * 60 * 60)
        super().__init__("auth_sessions", __name__, url_prefix=url_prefix)

    # region --- Helper methods ---

    def _issue_tokens(self, user: User, *, prev_refresh_jti: Optional[str] = None) -> Dict[str, Any]:
        # Generates a new access and refresh token (refresh rotated and stored in SessionsStorage).
        # Returns a payload ready to be sent to the client.
        now = int(time.time())

        access_payload = AccessTokenPayload(
            typ="access",
            jti=str(uuid.uuid4()),
            sub=user.id,
            nam=user.name,
            lvl=user.level,
            iat=now,
            exp=now + self.ACCESS_TTL,
        ).to_dict()

        refresh_payload = RefreshTokenPayload(
            typ="refresh",
            jti=str(uuid.uuid4()),
            sub=user.id,
            iat=now,
            exp=now + self.REFRESH_TTL,
        ).to_dict()

        access_token = self.serializer.dumps(access_payload)
        refresh_token = self.serializer.dumps(refresh_payload)

        # Rejestr/rotacja refresh tokenów
        self.sessions.rotate_refresh(prev_refresh_jti, refresh_payload["jti"], user.id, refresh_payload["exp"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.ACCESS_TTL,
            "user": user.to_public(),
        }

    def _load_token(self, token: str, *, max_age: Optional[int] = None) -> Dict[str, Any]:
        # Reads and verifies the token signature. Throws ValueError('expired'|'invalid') on errors.
        try:
            payload = self.serializer.loads(token, max_age=max_age)
            return payload
        except SignatureExpired:
            raise ValueError("expired")
        except BadSignature:
            raise ValueError("invalid")
    
    def _read_bearer(self) -> Optional[str]:
        # Gets the token from the Authorization: Bearer <token> header.
        auth = request.headers.get("Authorization", "")
        if not auth:
            return None

        # Normalize URL-encoded variant (some proxies/clients)
        raw = auth.strip()
        raw = raw.replace("Bearer%20", "Bearer ")

        # Peel off any number of leading "Bearer " (handles 'Bearer Bearer <token>')
        while raw.lower().startswith("bearer "):
            raw = raw[7:].lstrip()

        # Drop surrounding quotes if present
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            raw = raw[1:-1].strip()

        if not raw:
            return None

        return raw

    # endregion --- Helper methods ---

    @auto_swag(
        tags=["auth"],
        summary="Login — issue access & refresh tokens (Bearer)",
        security=[],    # Public
        request_body=request_body_json(
            {
                "type": "object",
                "properties": {"name": {"type": "string"}, "password": {"type": "string"}},
                "required": ["name", "password"]
            }
        ),
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                        "token_type": {"type": "string", "example": "Bearer"},
                        "expires_in": {"type": "integer", "example": 900},
                        "user": User.schema_public()
                    }
                }
            ),
            401: unauthorized("Invalid credentials"),
            400: bad_request("Invalid payload")
        }
    )
    def login(self):
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        password = data.get("password")

        if not isinstance(name, str) or not isinstance(password, str):
            return jsonify({"message": "invalid payload"}), 400

        user = self.users.verify_credentials(name, password)
        if not user:
            return jsonify({"message": "invalid credentials"}), 401

        return jsonify(self._issue_tokens(user)), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Refresh — rotate refresh token and issue new access token",
        security=[],    # Public
        request_body=request_body_json(
            {
                "type": "object",
                "properties": {"refresh_token": {"type": "string"}},
                "required": ["refresh_token"]
            }
        ),
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                        "token_type": {"type": "string"},
                        "expires_in": {"type": "integer"},
                        "user": User.schema_public(),
                    }
                }
            ),
            401: unauthorized("Invalid or expired refresh token"),
        }
    )
    def refresh(self):
        data = request.get_json(silent=True) or {}
        rtok = data.get("refresh_token")
        if not isinstance(rtok, str) or not rtok:
            return jsonify({"message": "invalid payload"}), 400

        # Decode and verify refresh payload
        try:
            raw = self._load_token(rtok, max_age=self.REFRESH_TTL)
            payload = RefreshTokenPayload.from_dict(raw)
        except ValueError:
            return jsonify({"message": "invalid or expired refresh token"}), 401

        uid, jti = payload.sub, payload.jti

        # Checking SessionsStorage (revoked/expired)
        if not self.sessions.is_valid(jti, uid):
            return jsonify({"message": "refresh token revoked or unknown"}), 401

        user = self.users.get_by_id(uid)
        if not user:
            return jsonify({"message": "user not found"}), 401

        out = self._issue_tokens(user, prev_refresh_jti=jti)
        return jsonify(out), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Validate access token (Authorization: Bearer)",
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "user": User.schema_public(),
                        "token": {"type": "object"}
                    }
                }
            ),
            401: unauthorized("Invalid or expired token"),
        },
    )
    def validate(self):
        try:
            user, payload_model = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({"message": "invalid or expired token"}), 401

        return jsonify({"valid": True, "user": user.to_public(), "token": payload_model.to_dict()}), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Logout — revoke provided refresh token (body or Authorization header)",
        security=[],    # Public
        request_body=request_body_json(
            {
                "type": "object",
                "properties": {
                    "refresh_token": {"type": "string"}
                }
            },
            required=False
        ),
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "revoked": {"type": "boolean"}
                    }
                }
            ),
            401: unauthorized("Invalid refresh token")}
    )
    def logout(self):
        # Prefer refresh_token from body and also allow Bearer (e.g. CLI clients)
        data = request.get_json(silent=True) or {}
        rtok = data.get("refresh_token") or self._read_bearer()
        if not isinstance(rtok, str) or not rtok:
            return jsonify({"message": "missing refresh token"}), 400

        try:
            raw = self._load_token(rtok, max_age=self.REFRESH_TTL)
            payload = RefreshTokenPayload.from_dict(raw)
        except ValueError:
            return jsonify({"message": "invalid or expired refresh token"}), 401

        # Idempotentnie — jeśli już nieważny, zwracamy sukces
        if not self.sessions.is_valid(payload.jti, payload.sub):
            return jsonify({"revoked": True}), 200

        self.sessions.revoke(payload.jti)
        return jsonify({"revoked": True}), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Who am I — return current user from access token",
        responses={
            200: ok(User.schema_public()),
            401: unauthorized("Invalid or missing token")
        },
    )
    def me(self):
        try:
            user, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({"message": "invalid or expired token"}), 401

        return jsonify(user.to_public()), 200
    
    # region --- Endpoint registration ---

    def register_routes(self) -> "SessionsController":
        self.add_url_rule("/login", view_func=self.login, methods=["POST"])
        self.add_url_rule("/refresh", view_func=self.refresh, methods=["POST"])
        self.add_url_rule("/validate", view_func=self.validate, methods=["POST"])
        self.add_url_rule("/logout", view_func=self.logout, methods=["POST"])
        self.add_url_rule("/me", view_func=self.me, methods=["GET"])
        return self

    # endregion --- Endpoint registration ---
