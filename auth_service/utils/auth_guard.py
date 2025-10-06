from typing import Optional, Tuple, Dict, Any
from flask import request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from auth_service.models.user import User
from auth_service.models.access_token_payload import AccessTokenPayload
from auth_service.storage.users_storage import UsersStorage
from auth_service import config


class AuthGuard:
    def __init__(self, users: Optional[UsersStorage] = None) -> None:
        self.users = users or UsersStorage()
        self.serializer = URLSafeTimedSerializer(config.SECRET, salt="auth-tokens")
        self.ACCESS_TTL = getattr(config, "ACCESS_TOKEN_SECONDS", 15 * 60)
    
    # region --- Token helper methods ---

    @staticmethod
    def read_bearer() -> Optional[str]:
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

        return raw or None
    
    def load_access(self, token: str) -> Dict[str, Any]:
        # Decodes and validates an access token, returning a payload (dict).
        # Throws ValueError('expired'|'invalid') on error.
        try:
            return self.serializer.loads(token, max_age=self.ACCESS_TTL)
        except SignatureExpired:
            raise ValueError("expired")
        except BadSignature:
            raise ValueError("invalid")
    
    def require_auth(self) -> Tuple[User, AccessTokenPayload]:
        # Requires a valid access token.
        # Returns: (User, AccessTokenPayload)
        # Throws PermissionError if unauthorized.
        atok = self.read_bearer()
        if not atok:
            raise PermissionError("missing bearer")

        try:
            raw = self.load_access(atok)
            payload = AccessTokenPayload.from_dict(raw)
        except Exception as e:
            raise PermissionError("invalid token")

        actor = self.users.get_user_by_id(payload.sub)
        if not actor:
            raise PermissionError("user not found")

        return actor, payload

    # endregion --- Token helper methods ---

    # region --- Role Helpers ---

    @staticmethod
    def is_root(user: User) -> bool:
        return user.level == User.LEVEL_ROOT

    @staticmethod
    def is_admin(user: User) -> bool:
        return user.level == User.LEVEL_ADMIN

    @staticmethod
    def is_user(user: User) -> bool:
        return user.level == User.LEVEL_USER

    # endregion --- Role Helpers ---
    