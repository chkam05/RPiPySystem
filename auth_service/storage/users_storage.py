import json
import os
import tempfile
import uuid
from typing import Any, Dict, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

from auth_service.models.user import User
from auth_service.config import db_path, DEFAULT_USERS, USERS_STORAGE_NAME


class UsersStorage:
    KEY_USERS: str = 'users'

    def __init__(self, path: str | None = None) -> None:
        self.db_path = path or db_path(USERS_STORAGE_NAME)

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        if not os.path.exists(self.db_path):
            self._atomic_write(self._build_initial_data())

    # region --- FileSystem Helpers ---

    def _build_initial_data(self) -> Dict[str, Any]:
        users: List[Dict[str, Any]] = []
        for u in DEFAULT_USERS:
            item = dict(u)
            item.setdefault(User.FIELD_ID, str(uuid.uuid4()))
            item.setdefault(User.FIELD_LEVEL, User.LEVEL_USER)
            users.append(item)
        return {self.KEY_USERS: users}

    def _read(self) -> Dict[str, Any]:
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._build_initial_data()

    def _atomic_write(self, data: Dict[str, Any]) -> None:
        dirpath = os.path.dirname(self.db_path) or "."
        with tempfile.NamedTemporaryFile("w", delete=False, dir=dirpath, encoding="utf-8") as tf:
            json.dump(data, tf, ensure_ascii=False, indent=2)
            tmp_name = tf.name
        os.replace(tmp_name, self.db_path)
    
    # endregion --- FileSystem Helpers ---

    # region --- Users CRUD ---

    def add_user(self, name: str, raw_password: str, *, level: str = User.LEVEL_USER) -> User:
        if self.get_by_name(name):
            raise ValueError('user_exists')
        
        uid = str(uuid.uuid4())
        pwd_hash = generate_password_hash(raw_password)

        user = User(id=uid, name=name, password_hash=pwd_hash, level=level)
        blob = self._read()
        users = blob.setdefault(self.KEY_USERS, [])
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

    def list_users(self) -> List[User]:
        blob = self._read()
        return [User.from_dict(u) for u in blob.get(self.KEY_USERS, [])]

    def remove_user(self, uid: str) -> bool:
        blob = self._read()
        users = blob.get(self.KEY_USERS, [])
        new_users = [u for u in users if u.get(User.FIELD_ID) != uid]

        if len(new_users) == len(users):
            return False
        
        blob[self.KEY_USERS] = new_users
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
            if name != current.get(User.FIELD_NAME) and self.get_by_name(name):
                raise ValueError('user_exists')
            current[User.FIELD_NAME] = name

        if raw_password is not None:
            current[User.FIELD_PASSWORD_HASH] = generate_password_hash(raw_password)
        
        if level is not None:
            if level not in User.get_levels():
                raise ValueError('invalid_level')
            current[User.FIELD_LEVEL] = level

        users[idx] = current
        blob[self.KEY_USERS] = users
        self._atomic_write(blob)
        return User.from_dict(current)

    # endregion --- Users CRUD ---

    # region --- Auth Helper ---

    def verify_credentials(self, name: str, raw_password: str) -> Optional[User]:
        user = self.get_user_by_name(name)
        if user and check_password_hash(user.password_hash, raw_password):
            return user
        return None

    # endregion --- Auth Helper ---
