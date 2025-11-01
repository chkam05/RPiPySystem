from typing import Any, ClassVar, Dict, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from auth_service.config import DEFAULT_USERS
from auth_service.models.access_level import AccessLevel
from auth_service.models.user import User
from utils.base_json_storage import BaseJsonStorage


class UsersStorage(BaseJsonStorage):
    KEY_USERS: ClassVar[str] = 'users'

    def __init__(self, path: str | None, *, enable_cache: bool = True) -> None:
        super().__init__(path, enable_cache=enable_cache)

    def _build_initial_data(self) -> Dict[str, Any]:
        return {self.KEY_USERS: [u.copy() for u in DEFAULT_USERS]}
    
    # --- Users CRUD methods ---

    def add_user(self, name: str, raw_password: str, *, level: str = AccessLevel.USER.value) -> User:
        if self.get_user_by_name(name):
            raise ValueError('user_exists')
        
        blob = self._read()
        users = blob.setdefault(self.KEY_USERS, [])
        
        uid = str(uuid.uuid4())
        pwd_hash = generate_password_hash(raw_password)
        user = User(id=uid, name=name, password_hash=pwd_hash, level=AccessLevel.from_str(level))
        
        users.append(user.to_dict())
        self._atomic_write(blob)
        return user
    
    def get_user_by_id(self, uid: str) -> Optional[User]:
        for u in self.list_users():
            if u.id == uid:
                return u
        return None

    def get_user_by_name(self, name: str) -> Optional[User]:
        for u in self.list_users():
            if u.name == name:
                return u
        return None

    @staticmethod
    def _filter_user(
            u: Dict[str, Any],
            f_name: Optional[str] = None,
            f_level: Optional[str] = None) -> bool:
        name_val = str(u.get(User.FIELD_NAME, ''))
        level_val = str(u.get(User.FIELD_LEVEL, ''))
        
        if f_name:
            nf = f_name.lower()
            if nf not in name_val.lower():
                return False
        
        if f_level:
            lf = f_level.lower()
            if lf != level_val.lower():
                return False
        
        return True
    
    def list_users(
            self,
            f_name: Optional[str] = None,
            f_level: Optional[str] = None) -> List[User]:
        blob = self._read()
        users = blob.get(self.KEY_USERS, [])
        
        filtered = [u for u in users if self._filter_user(u, f_name, f_level)]
        return [User.from_dict(u) for u in filtered]

    def remove_user(self, uid: str) -> bool:
        blob = self._read()
        users = blob.get(self.KEY_USERS, [])

        match_users = [u for u in users if u.get(User.FIELD_ID) != uid]

        if len(match_users) == len(users):
            return False
        
        blob[self.KEY_USERS] = match_users
        self._atomic_write(blob)
        return True
    
    def update_user(
            self,
            uid: str,
            *,
            name: Optional[str] = None,
            raw_password: Optional[str] = None,
            level: Optional[str] = None) -> Optional[User]:
        blob = self._read()
        users = blob.get(self.KEY_USERS, [])

        # Locate user by constant field name
        idx = next((i for i, u in enumerate(users) if u.get(User.FIELD_ID) == uid), None)
        if idx is None:
            return None

        current = users[idx]

        if name is not None:
            if name != current.get(User.FIELD_NAME) and self.get_user_by_name(name):
                raise ValueError('user_exists')
            current[User.FIELD_NAME] = name

        if raw_password is not None:
            current[User.FIELD_PASSWORD_HASH] = generate_password_hash(raw_password)
        
        if level is not None:
            access_level = AccessLevel.from_str(level)
            current[User.FIELD_LEVEL] = access_level

        users[idx] = current
        blob[self.KEY_USERS] = users
        self._atomic_write(blob)
        return User.from_dict(current)

    # --- Authentication Helper methods ---

    def verify_credentials(self, name: str, raw_password: str) -> Optional[User]:
        user = self.get_user_by_name(name)
        if user and check_password_hash(user.password_hash, raw_password):
            return user
        return None