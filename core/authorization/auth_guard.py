import time
import uuid

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from typing import Any, ClassVar, Dict, Optional, Tuple

from .bearer_reader import BearerReader
from .enums.access_level import AccessLevel
from .models.access_token import AccessToken
from .models.refresh_token import RefreshToken
from .models.token_pair import TokenPair
from .models.user import User
from .storage.session_storage import SessionStorage
from .storage.user_storage import UserStorage


class AuthGuard:
    _SALT_NAME: ClassVar[str] = 'auth-tokens'

    def __init__(self, at_seconds: int, rt_seconds: int, secret: str, session_storage: SessionStorage, user_storage: UserStorage):
        # Fields validation:
        if not isinstance(at_seconds, int) or at_seconds <= 0:
            raise ValueError('"at_seconds" (access token validation time in seconds) must be a positive integer.')
        if not isinstance(rt_seconds, int) or rt_seconds <= 0:
            raise ValueError('"rt_seconds" (refresh token validation time in seconds) must be a positive integer.')
        if not secret:
            raise ValueError('"secret" is required.')
        if not session_storage:
            raise ValueError('"session_storage" is required.')
        if not user_storage:
            raise ValueError('"user_storage" is required.')
        
        self._ACCESS_TTL = at_seconds
        self._REFRESH_TTL = rt_seconds
        self._serializer = URLSafeTimedSerializer(secret, salt=self._SALT_NAME)
        self._session_storage = session_storage
        self._user_storage = user_storage

    # --------------------------------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------------------------------

    @property
    def session_storage(self) -> SessionStorage:
        """Return the session storage."""
        return self._session_storage

    @property
    def user_storage(self) -> UserStorage:
        """Return the user storage."""
        return self._user_storage
    
    # --------------------------------------------------------------------------------
    # AccessLevel helpers
    # --------------------------------------------------------------------------------

    @classmethod
    def is_root(cls, user: User) -> bool:
        cls.validate_access(user, AccessLevel.ROOT)

    @classmethod
    def is_admin(cls, user: User) -> bool:
        cls.validate_access(user, AccessLevel.ADMIN)

    @classmethod
    def is_user(cls, user: User) -> bool:
        cls.validate_access(user, AccessLevel.USER)

    @staticmethod
    def validate_access(user: User, access_level: AccessLevel) -> bool:
        return user.level == access_level

    # --------------------------------------------------------------------------------
    # Token helpers
    # --------------------------------------------------------------------------------

    def issue_tokens(self, user: User, *, prev_refresh_jti: Optional[str] = None) -> TokenPair:
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
            exp=now + self._ACCESS_TTL,
        ).to_dict()

        refresh_payload = RefreshToken(
            typ='refresh',
            jti=str(uuid.uuid4()),
            sub=user.id,
            iat=now,
            exp=now + self._REFRESH_TTL,
        ).to_dict()

        access_token = self._serializer.dumps(access_payload)
        refresh_token = self._serializer.dumps(refresh_payload)

        # Register/rotation, tokens refresh
        self._session_storage.rotate_refresh(
            prev_refresh_jti,
            refresh_payload['jti'],
            user.id,
            refresh_payload['exp'],
            access_jti=access_payload['jti'],
            access_expires_at=access_payload['exp'])

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='Bearer',
            expires_in=self._ACCESS_TTL,
            user=user,
        )

    def load_access(self, token: str) -> Dict[str, Any]:
        """
        Decodes and verifies an access token. Returns a payload (dict).
        """
        try:
            return self._serializer.loads(token, max_age=self._ACCESS_TTL)
        except SignatureExpired:
            raise ValueError('expired')
        except BadSignature:
            raise ValueError('invalid')
    
    def load_refresh(self, token: str) -> Dict[str, Any]:
        """
        Decodes and verifies the refresh token. Returns the payload (dict).
        """
        try:
            return self._serializer.loads(token, max_age=self._REFRESH_TTL)
        except SignatureExpired:
            raise ValueError('expired')
        except BadSignature:
            raise ValueError('invalid')
    
    def require_auth(self) -> Tuple[User, AccessToken]:
        atok = BearerReader.read_bearer_from_request()
        if not atok:
            raise PermissionError('Missing Bearer access token.')
        
        try:
            raw = self.load_access(atok)
            payload = AccessToken.from_dict(raw)
        except Exception as e:
            raise PermissionError('Invalid token.')
        
        if self._session_storage.is_access_revoked(payload.jti):
            raise PermissionError('Revoked token.')

        actor = self._user_storage.get_user_by_id(payload.sub)
        if not actor:
            raise PermissionError('User not found.')

        return actor, payload
    
    def revoke(
            self,
            refresh_jti: Optional[str] = None,
            access_jti: Optional[str] = None,
            access_expires_at: Optional[int] = None
        ) -> bool:
        """
        Revokes refresh and access tokens when provided.
        """
        revoked = False

        if refresh_jti:
            revoked = self.session_storage.revoke(
                refresh_jti,
                access_jti=access_jti,
                access_expires_at=access_expires_at)
        elif access_jti:
            revoked = self.session_storage.revoke_access(access_jti, expires_at=access_expires_at)

        return revoked

    def update_last_login(self, user_uid: str) -> None:
        self._user_storage.update_last_login(user_uid)

    # --------------------------------------------------------------------------------
    # Validation methods
    # --------------------------------------------------------------------------------

    def is_valid_refresh_token(self, jti: str, user_id: str) -> bool:
        return self.session_storage.is_valid(jti, user_id)
    
    def is_valid_access_token(self, jti: str) -> bool:
        return self.session_storage.is_valid_access(jti)

    def verify_credentials(self, name: str, password: str) -> Optional[User]:
        return self.user_storage.verify_credentials(name, password)
    
