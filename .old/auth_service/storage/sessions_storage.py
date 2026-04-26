import time
from typing import Any, ClassVar, Dict, List, Optional

from auth_service.models.refresh_token_record import RefreshTokenRecord
from utils.base_json_storage import BaseJsonStorage


class SessionsStorage(BaseJsonStorage):
    KEY_REFRESH_TOKENS: ClassVar[str] = 'refresh_tokens'

    def __init__(self, path: str | None, *, enable_cache: bool = True) -> None:
        super().__init__(path, enable_cache=enable_cache)
    
    def _build_initial_data(self) -> Dict[str, Any]:
        return {self.KEY_REFRESH_TOKENS: []}
    
    # --- Registry API methods ---

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
                    # Mark as revoked, keeping other fields
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
    
    # --- Additional Helper methods ---

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