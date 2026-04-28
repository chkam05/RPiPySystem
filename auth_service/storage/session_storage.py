from typing import Any, ClassVar, Dict, List, Optional
import time

from auth_service.models.refresh_token_record import RefreshTokenRecord
from core.data.json_storage import JsonStorage


class SessionStorage(JsonStorage):
    KEY_REFRESH_TOKENS: ClassVar[str] = 'refresh_tokens'
    KEY_REVOKED_ACCESS_TOKENS: ClassVar[str] = 'revoked_access_tokens'

    def __init__(self, path: str | None, *, enable_cache: bool = True) -> None:
        super().__init__(path, enable_cache=enable_cache)
    
    def _build_initial_data(self) -> Dict[str, Any]:
        return {self.KEY_REFRESH_TOKENS: [], self.KEY_REVOKED_ACCESS_TOKENS: []}
    
    # --------------------------------------------------------------------------------
    # Registry API methods
    # --------------------------------------------------------------------------------

    def add_refresh(
            self,
            jti: str,
            user_id: str,
            expires_at: int,
            access_jti: Optional[str] = None,
            access_expires_at: Optional[int] = None) -> None:
        record = RefreshTokenRecord(
            jti=jti,
            uid=user_id,
            exp=expires_at,
            revoked=False,
            access_jti=access_jti,
            access_exp=access_expires_at)
        blob = self._read()
        items = blob.setdefault(self.KEY_REFRESH_TOKENS, [])
        items.append(record.to_dict())
        self._atomic_write(blob)
    
    def rotate_refresh(
            self,
            old_jti: Optional[str],
            new_jti: str,
            user_id: str,
            expires_at: int,
            access_jti: Optional[str] = None,
            access_expires_at: Optional[int] = None) -> None:
        blob = self._read()
        items: List[Dict[str, Any]] = blob.setdefault(self.KEY_REFRESH_TOKENS, [])
        revoked_access_tokens: List[Dict[str, Any]] = blob.setdefault(self.KEY_REVOKED_ACCESS_TOKENS, [])

        if old_jti:
            for i, it in enumerate(items):
                rec = RefreshTokenRecord.from_dict(it)
                if rec.jti == old_jti:
                    # Mark as revoked, keeping other fields
                    rec.revoked = True
                    items[i] = rec.to_dict()
                    self._append_revoked_access(revoked_access_tokens, rec.access_jti, rec.uid, rec.access_exp)
                    break

        new_rec = RefreshTokenRecord(
            jti=new_jti,
            uid=user_id,
            exp=expires_at,
            revoked=False,
            access_jti=access_jti,
            access_exp=access_expires_at)
        items.append(new_rec.to_dict())
        self._atomic_write(blob)
    
    def revoke(self, jti: str, access_jti: Optional[str] = None, access_expires_at: Optional[int] = None) -> bool:
        blob = self._read()
        items: List[Dict[str, Any]] = blob.get(self.KEY_REFRESH_TOKENS, [])
        revoked_access_tokens: List[Dict[str, Any]] = blob.setdefault(self.KEY_REVOKED_ACCESS_TOKENS, [])
        revoked = False

        for i, it in enumerate(items):
            rec = RefreshTokenRecord.from_dict(it)
            if rec.jti == jti and not rec.revoked:
                rec.revoked = True
                items[i] = rec.to_dict()
                revoked = True
                self._append_revoked_access(revoked_access_tokens, rec.access_jti, rec.uid, rec.access_exp)
                break
        
        if access_jti:
            revoked = self._append_revoked_access(revoked_access_tokens, access_jti, None, access_expires_at) or revoked

        if revoked:
            self._atomic_write(blob)
        return revoked

    def revoke_access(self, jti: str, user_id: Optional[str] = None, expires_at: Optional[int] = None) -> bool:
        blob = self._read()
        revoked_access_tokens: List[Dict[str, Any]] = blob.setdefault(self.KEY_REVOKED_ACCESS_TOKENS, [])

        if not self._append_revoked_access(revoked_access_tokens, jti, user_id, expires_at):
            return False

        self._atomic_write(blob)
        return True
    
    def is_valid(self, jti: str, user_id: str) -> bool:
        now = int(time.time())
        items: List[Dict[str, Any]] = self._read().get(self.KEY_REFRESH_TOKENS, [])

        for it in items:
            rec = RefreshTokenRecord.from_dict(it)
            if rec.jti == jti and rec.uid == user_id and rec.is_valid(now):
                return True
        return False

    def is_access_revoked(self, jti: str) -> bool:
        now = int(time.time())
        blob = self._read()
        items: List[Dict[str, Any]] = blob.get(self.KEY_REVOKED_ACCESS_TOKENS, [])

        return any(
            it.get('jti') == jti and int(it.get('exp', now + 1)) > now
            for it in items
        )
    
    def is_valid_access(self, jti: str) -> bool:
        return not self.is_access_revoked(jti)
    
    # --------------------------------------------------------------------------------
    # Utilities
    # --------------------------------------------------------------------------------

    def get_refresh(self, jti: str) -> Optional[RefreshTokenRecord]:
        items: List[Dict[str, Any]] = self._read().get(self.KEY_REFRESH_TOKENS, [])

        for it in items:
            rec = RefreshTokenRecord.from_dict(it)
            if rec.jti == jti:
                return rec
        return None
    
    def get_refresh_by_access_jti(self, access_jti: str) -> Optional[RefreshTokenRecord]:
        items: List[Dict[str, Any]] = self._read().get(self.KEY_REFRESH_TOKENS, [])

        for it in items:
            rec = RefreshTokenRecord.from_dict(it)
            if rec.access_jti == access_jti:
                return rec
        return None

    def list_refresh_tokens(self, user_id: Optional[str] = None) -> List[RefreshTokenRecord]:
        items: List[Dict[str, Any]] = self._read().get(self.KEY_REFRESH_TOKENS, [])
        out = [RefreshTokenRecord.from_dict(it) for it in items]

        if user_id is not None:
            out = [r for r in out if r.uid == user_id]
        return out

    @staticmethod
    def _append_revoked_access(
            items: List[Dict[str, Any]],
            jti: Optional[str],
            user_id: Optional[str],
            expires_at: Optional[int]
        ) -> bool:
        if not jti:
            return False
        if any(it.get('jti') == jti for it in items):
            return False

        record: Dict[str, Any] = {'jti': jti}
        if user_id:
            record['uid'] = user_id
        if expires_at is not None:
            record['exp'] = expires_at

        items.append(record)
        return True
