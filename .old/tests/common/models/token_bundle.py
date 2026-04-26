from dataclasses import dataclass
import time
from typing import Optional


@dataclass
class TokenBundle:
    access_token: str
    expires_in: Optional[float] = None
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and (time.time() + 30) >= self.expires_at