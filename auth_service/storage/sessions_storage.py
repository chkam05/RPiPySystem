import json
import os
import tempfile
from typing import Any, Dict, List, Optional
import time

from auth_service.config import db_path, SESSIONS_STORAGE_NAME
from auth_service.models.refresh_token_record import RefreshTokenRecord


class SessionsStorage:
    KEY_REFRESH_TOKENS: str = "refresh_tokens"

    def __init__(self, path: str | None = None) -> None:
        self.db_path = path or db_path(SESSIONS_STORAGE_NAME)

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        if not os.path.exists(self.db_path):
            self._atomic_write(self._build_initial_data())
    
    # region --- FileSystem Helpers ---

    def _build_initial_data(self) -> Dict[str, Any]:
        return {self.KEY_REFRESH_TOKENS: []}
    
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

    # region --- Registry API ---

    def add_refresh(self, jti: str, user_id: str, expires_at: int) -> None:
        record = RefreshTokenRecord(jti=jti, uid=user_id, exp=expires_at, revoked=False)
        blob = self._read()
        items = blob.setdefault(self.KEY_REFRESH_TOKENS, [])
        items.append(record.to_dict())
        self._atomic_write(blob)
    
    def rotate_refresh(self, old_jti: Optional[str], new_jti: str, user_id: str, expires_at: int) -> None:
        blob = self._read()
        items: List[Dict[str, Any]] = blob.setdefault(self.KEY_REFRESH_TOKENS, [])

        if old_jti:
            for i, it in enumerate(items):
                rec = RefreshTokenRecord.from_dict(it)
                if rec.jti == old_jti:
                    # zaznacz jako revoked, zachowując pozostałe pola
                    rec.revoked = True
                    items[i] = rec.to_dict()
                    break

        new_rec = RefreshTokenRecord(jti=new_jti, uid=user_id, exp=expires_at, revoked=False)
        items.append(new_rec.to_dict())
        self._atomic_write(blob)
    
    def revoke(self, jti: str) -> bool:
        blob = self._read()
        items: List[Dict[str, Any]] = blob.get(self.KEY_REFRESH_TOKENS, [])

        for i, it in enumerate(items):
            rec = RefreshTokenRecord.from_dict(it)
            if rec.jti == jti and not rec.revoked:
                rec.revoked = True
                items[i] = rec.to_dict()
                self._atomic_write(blob)
                return True
        return False

    def is_valid(self, jti: str, user_id: str) -> bool:
        now = int(time.time())
        items: List[Dict[str, Any]] = self._read().get(self.KEY_REFRESH_TOKENS, [])

        for it in items:
            rec = RefreshTokenRecord.from_dict(it)
            if rec.jti == jti and rec.uid == user_id and rec.is_valid(now):
                return True
        return False

    # endregion --- Registry API ---

    # region --- Additional helper methods ---

    def list_refresh_tokens(self, user_id: Optional[str] = None) -> List[RefreshTokenRecord]:
        items: List[Dict[str, Any]] = self._read().get(self.KEY_REFRESH_TOKENS, [])
        out = [RefreshTokenRecord.from_dict(it) for it in items]

        if user_id is not None:
            out = [r for r in out if r.uid == user_id]
        return out

    def get_refresh(self, jti: str) -> Optional[RefreshTokenRecord]:
        items: List[Dict[str, Any]] = self._read().get(self.KEY_REFRESH_TOKENS, [])

        for it in items:
            rec = RefreshTokenRecord.from_dict(it)
            if rec.jti == jti:
                return rec
        return None

    # endregion --- Additional helper methods ---
