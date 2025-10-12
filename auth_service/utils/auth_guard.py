from typing import Any, ClassVar, Dict, Tuple
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from auth_service.models.access_level import AccessLevel
from auth_service.models.access_token import AccessToken
from auth_service.models.user import User
from auth_service.storage.users_storage import UsersStorage
from utils.security import SecurityUtils


class AuthGuard:
    _SALT_NAME: ClassVar[str] = 'auth-tokens'

    def __init__(self, at_seconds: int, rt_seconds: int, secret: str, users_storage: UsersStorage):
        # Fields validation:
        if not isinstance(at_seconds, int) or at_seconds <= 0:
            raise ValueError('at_seconds (access token validation time in seconds) must be a positive integer.')
        if not isinstance(rt_seconds, int) or rt_seconds <= 0:
            raise ValueError('rt_seconds (refresh token validation time in seconds) must be a positive integer.')
        if not secret:
            raise ValueError('secret is required.')
        if not users_storage:
            raise ValueError('users_storage is required.')
        
        self.ACCESS_TTL = at_seconds
        self.REFRESH_TTL = rt_seconds
        self.serializer = URLSafeTimedSerializer(secret, salt=self._SALT_NAME)
        self.users_storage = users_storage
    
    # --- Token Helper methods ---

    def load_access(self, token: str) -> Dict[str, Any]:
        """
        Decodes and verifies an access token. Returns a payload (dict).
        """
        try:
            return self.serializer.loads(token, max_age=self.ACCESS_TTL)
        except SignatureExpired:
            raise ValueError('expired')
        except BadSignature:
            raise ValueError('invalid')
    
    def load_refresh(self, token: str) -> Dict[str, Any]:
        """
        Decodes and verifies the refresh token. Returns the payload (dict).
        """
        try:
            return self.serializer.loads(token, max_age=self.REFRESH_TTL)
        except SignatureExpired:
            raise ValueError('expired')
        except BadSignature:
            raise ValueError('invalid')
    
    def require_auth(self) -> Tuple[User, AccessToken]:
        atok = SecurityUtils.read_bearer_from_request()
        if not atok:
            raise PermissionError('missing bearer')
        
        try:
            raw = self.load_access(atok)
            payload = AccessToken.from_dict(raw)
        except Exception as e:
            raise PermissionError('invalid token')

        actor = self.users_storage.get_user_by_id(payload.sub)
        if not actor:
            raise PermissionError('user not found')

        return actor, payload
    
    # --- Role Helpers ---

    @staticmethod
    def is_root(user: User) -> bool:
        return user.level == AccessLevel.ROOT

    @staticmethod
    def is_admin(user: User) -> bool:
        return user.level == AccessLevel.ADMIN

    @staticmethod
    def is_user(user: User) -> bool:
        return user.level == AccessLevel.USER