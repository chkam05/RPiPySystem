from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from tests.common.authenticator import Authenticator


class HttpClient:
    
    def __init__(
            self,
            base_address: str,
            authenticator: Optional[Authenticator] = None,
            default_headers: Optional[Dict[str, str]] = None,
            timeout: int = 30
    ) -> None:
        self._base_address = base_address.rstrip('/')
        self._authenticator = authenticator
        self._default_headers = default_headers or {}
        self._timeout = timeout
        self._session = requests.Session()
    
    def _build_url(self, path: str) -> str:
        if path.startswith('http://') or path.startswith('https://'):
            return path
        return urljoin(self._base_address + '/', path.lstrip('/'))
    
    def _request(
        self,
        method: str,
        path: str,
        *,
        use_auth: bool,
        content: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        url = self._build_url(path)

        merged_headers: Dict[str, str] = dict(self._default_headers)
        if headers:
            merged_headers.update(headers)

        if use_auth:
            if not self._authenticator:
                raise RuntimeError('use_auth=True, ale nie przekazano Authenticatora.')
            token = self._authenticator.get_access_token()
            merged_headers.setdefault('Authorization', f'Bearer {token}')

        data = None
        if content is not None:
            merged_headers.setdefault('Content-Type', 'application/json; charset=utf-8')
            data = content.encode('utf-8') if isinstance(content, str) else content

        resp = self._session.request(
            method=method.upper(),
            url=url,
            params=params or {},
            data=data,
            headers=merged_headers,
            timeout=self._timeout,
            verify=False
        )
        return resp
    
    def get(
            self,
            path: str,
            *,
            use_auth: bool = False,
            headers: Optional[Dict[str, str]] = None,
            **params: Any
    ) -> requests.Response:
        return self._request('GET', path, use_auth=use_auth, headers=headers, params=params)

    def post(
            self,
            path: str,
            *,
            use_auth: bool = False,
            content: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
            **params: Any
    ) -> requests.Response:
        return self._request('POST', path, use_auth=use_auth, content=content, headers=headers, params=params)

    def put(
            self,
            path: str,
            *,
            use_auth: bool = False,
            content: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
            **params: Any
    ) -> requests.Response:
        return self._request('PUT', path, use_auth=use_auth, content=content, headers=headers, params=params)

    def patch(
            self,
            path: str,
            *,
            use_auth: bool = False,
            content: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
            **params: Any
    ) -> requests.Response:
        return self._request('PATCH', path, use_auth=use_auth, content=content, headers=headers, params=params)

    def delete(
            self,
            path: str,
            *,
            use_auth: bool = False,
            headers: Optional[Dict[str, str]] = None,
            **params: Any
    ) -> requests.Response:
        return self._request('DELETE', path, use_auth=use_auth, headers=headers, params=params)