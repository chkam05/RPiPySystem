from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib import error, request


class HttpClient:

    # --------------------------------------------------------------------------------
    # CONSTRUCTORS
    # --------------------------------------------------------------------------------

    def __init__(self, base_url: str, timeout: float = 5.0, token: Optional[str] = None) -> None:
        self._base_url = base_url.rstrip('/')
        self._timeout = timeout
        self._token = token

    # --------------------------------------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------------------------------------

    def get(self, path: str) -> Dict[str, Any] | list[Any] | None:
        return self._request('GET', path)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any] | list[Any] | None:
        return self._request('POST', path, data=data)

    # --------------------------------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------------------------------

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None):
        body = json.dumps(data).encode('utf-8') if data is not None else None
        headers = {'Accept': 'application/json'}
        if body is not None:
            headers['Content-Type'] = 'application/json'
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'

        req = request.Request(
            url=f'{self._base_url}/{path.strip("/")}',
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with request.urlopen(req, timeout=self._timeout) as resp:
                content = resp.read()
        except error.HTTPError as e:
            content = e.read()
            if not content:
                raise
        if not content:
            return None

        return json.loads(content.decode('utf-8'))
