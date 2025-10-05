from __future__ import annotations
import json
import os
import tempfile
import uuid
from typing import Dict, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from auth_service.models.user import User
from auth_service.config import DB_PATH, DEFAULT_USERS


class UsersStorage:
    # Collection key constant (top-level JSON key)
    KEY_USERS: str = 'users'

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        dir_name = os.path.dirname(self.db_path)

        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        if not os.path.exists(self.db_path):
            seed = []
            for u in DEFAULT_USERS:
                item = dict(u)
                item.setdefault(User.FIELD_ID, str(uuid.uuid4()))
                seed.append(item)
            self._atomic_write({self.KEY_USERS: seed})

    # --- FileSystem Helpers ---

    def _read(self) -> Dict:
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {self.KEY_USERS: []}

    def _atomic_write(self, data: Dict) -> None:
        # Atomic write using a temp file then replace to avoid partial writes
        dirpath = os.path.dirname(self.db_path) or '.'
        with tempfile.NamedTemporaryFile('w', delete=False, dir=dirpath, encoding='utf-8') as tf:
            json.dump(data, tf, ensure_ascii=False, indent=2)
            tmp_name = tf.name
        os.replace(tmp_name, self.db_path)

    # --- CRUD ---

    def list_users(self) -> List[User]:
        blob = self._read()
        return [User.from_dict(u) for u in blob.get(self.KEY_USERS, [])]

    def get_by_id(self, uid: str) -> Optional[User]:
        for u in self.list_users():
            if u.id == uid:
                return u
        return None

    def get_by_name(self, name: str) -> Optional[User]:
        for u in self.list_users():
            if u.name == name:
                return u
        return None

    def add(self, name: str, raw_password: str) -> User:
        # Enforce unique name
        if self.get_by_name(name):
            raise ValueError('user_exists')
        uid = str(uuid.uuid4())
        pwd_hash = generate_password_hash(raw_password)

        user = User(id=uid, name=name, password_hash=pwd_hash)
        blob = self._read()
        users = blob.setdefault(self.KEY_USERS, [])
        users.append(user.to_dict())
        self._atomic_write(blob)
        return user

    def update(self, uid: str, *, name: Optional[str] = None, raw_password: Optional[str] = None) -> Optional[User]:
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

        users[idx] = current
        blob[self.KEY_USERS] = users
        self._atomic_write(blob)
        return User.from_dict(current)

    def remove(self, uid: str) -> bool:
        blob = self._read()
        users = blob.get(self.KEY_USERS, [])
        new_users = [u for u in users if u.get(User.FIELD_ID) != uid]
        if len(new_users) == len(users):
            return False
        blob[self.KEY_USERS] = new_users
        self._atomic_write(blob)
        return True

    # --- Auth Helper ---

    def verify_credentials(self, name: str, raw_password: str) -> Optional[User]:
        user = self.get_by_name(name)
        if user and check_password_hash(user.password_hash, raw_password):
            return user
        return None