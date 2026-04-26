from typing import Dict, Optional

from flask import request


class BearerReader:
    """Static utility class for extracting Bearer tokens from HTTP requests."""

    def __new__(cls, *args, **kwargs):
        """Prevent instantiation of this static utility class."""
        raise TypeError(f'{cls.__name__} is a static class and cannot be instantiated.')
    
    @staticmethod
    def read_bearer_from_request() -> Optional[str]:
        """Extract and normalize a Bearer token from the incoming request headers."""
        auth = request.headers.get('Authorization', '')
        if not auth:
            return None
        
        auth = auth.strip().replace('Bearer%20', 'Bearer ')

        while auth.lower().startswith('bearer '):
            auth = auth[7:].lstrip()

        if (auth.startswith('"') and auth.endswith('"')) or (auth.startswith('\'') and auth.endswith('\'')):
            auth = auth[1:-1].strip()
        
        return auth or None
    
    @classmethod
    def bearer_headers_from_request(cls) -> Optional[Dict[str, str]]:
        """Return a dictionary with the extracted Bearer token formatted for outgoing headers."""
        token = cls.read_bearer_from_request()
        return {'Authorization': f'Bearer {token}'} if token else None