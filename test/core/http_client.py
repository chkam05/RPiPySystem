from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
import urllib3

from .authenticator import Authenticator


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HttpClient:
    """Small requests-based client for live API tests."""

    def __init__(
        self,
        base_address: str,
        authenticator: Optional[Authenticator] = None,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        verify_ssl: bool = False,
    ) -> None:
        self._base_address = base_address.rstrip('/')
        self._authenticator = authenticator
        self._default_headers = default_headers or {}
        self._timeout = timeout
        self._verify_ssl = verify_ssl
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
        use_auth: Optional[bool] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        content: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        merged_headers: Dict[str, str] = dict(self._default_headers)
        if headers:
            merged_headers.update(headers)

        should_use_auth = self._authenticator is not None if use_auth is None else use_auth
        if should_use_auth:
            if not self._authenticator:
                raise RuntimeError('use_auth=True, but no Authenticator was provided.')
            merged_headers.setdefault('Authorization', f'Bearer {self._authenticator.get_access_token()}')

        request_data = data
        if content is not None:
            merged_headers.setdefault('Content-Type', 'application/json; charset=utf-8')
            request_data = content.encode('utf-8') if isinstance(content, str) else content

        return self._session.request(
            method=method.upper(),
            url=self._build_url(path),
            params=params or {},
            json=json,
            data=request_data,
            headers=merged_headers,
            timeout=self._timeout,
            verify=self._verify_ssl,
        )

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        return self._request(method, path, **kwargs)

    def get(self, path: str, *, use_auth: Optional[bool] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self._request('GET', path, use_auth=use_auth, headers=headers, params=params)

    def post(self, path: str, *, use_auth: Optional[bool] = None, json: Optional[Any] = None, content: Optional[str] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self._request('POST', path, use_auth=use_auth, json=json, content=content, headers=headers, params=params)

    def put(self, path: str, *, use_auth: Optional[bool] = None, json: Optional[Any] = None, content: Optional[str] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self._request('PUT', path, use_auth=use_auth, json=json, content=content, headers=headers, params=params)

    def patch(self, path: str, *, use_auth: Optional[bool] = None, json: Optional[Any] = None, content: Optional[str] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self._request('PATCH', path, use_auth=use_auth, json=json, content=content, headers=headers, params=params)

    def update(self, path: str, *, use_auth: Optional[bool] = None, json: Optional[Any] = None, content: Optional[str] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self.patch(path, use_auth=use_auth, json=json, content=content, headers=headers, **params)

    def delete(self, path: str, *, use_auth: Optional[bool] = None, json: Optional[Any] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self._request('DELETE', path, use_auth=use_auth, json=json, headers=headers, params=params)

    def options(self, path: str, *, use_auth: Optional[bool] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self._request('OPTIONS', path, use_auth=use_auth, headers=headers, params=params)

    def head(self, path: str, *, use_auth: Optional[bool] = None, headers: Optional[Dict[str, str]] = None, **params: Any) -> requests.Response:
        return self._request('HEAD', path, use_auth=use_auth, headers=headers, params=params)
