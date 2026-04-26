from flask import request
from typing import Dict, Optional


class SecurityUtils:

    def __new__(cls, *args, **kwargs):
        raise TypeError(f'{cls.__name__} is a static class and cannot be instantiated.')

    @staticmethod
    def read_bearer_from_request() -> Optional[str]:
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
        token = cls.read_bearer_from_request()
        return {'Authorization': f'Bearer {token}'} if token else None
