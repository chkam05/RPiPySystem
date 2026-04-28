from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional
from urllib.parse import urljoin

import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class TokenBundle:
    access_token: str
    refresh_token: Optional[str]
    token_type: str = 'Bearer'


class Authenticator:
    LOGIN_ENDPOINT: ClassVar[str] = '/login'
    REFRESH_ENDPOINT: ClassVar[str] = '/refresh'
    LOGOUT_ENDPOINT: ClassVar[str] = '/logout'
    VALIDATE_ENDPOINT: ClassVar[str] = '/validate'

    def __init__(
        self,
        base_address: str,
        username: str,
        password: str,
        timeout: int = 30,
        verify_ssl: bool = False,
    ) -> None:
        self._base_address = base_address.rstrip('/')
        self._username = username
        self._password = password
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._session = requests.Session()
        self._tokens: Optional[TokenBundle] = None

    @property
    def tokens(self) -> Optional[TokenBundle]:
        return self._tokens

    def _build_url(self, path: str) -> str:
        return urljoin(self._base_address + '/', path.lstrip('/'))

    def _parse_tokens(self, data: Dict[str, Any]) -> TokenBundle:
        access = data.get('access_token')
        refresh = data.get('refresh_token')
        token_type = data.get('token_type', 'Bearer')

        if not access:
            raise ValueError('Missing "access_token" in API response.')
        if not refresh:
            raise ValueError('Missing "refresh_token" in API response.')

        return TokenBundle(access, refresh, token_type)

    def login(self) -> TokenBundle:
        response = self._session.post(
            self._build_url(self.LOGIN_ENDPOINT),
            json={'username': self._username, 'password': self._password},
            timeout=self._timeout,
            verify=self._verify_ssl,
        )
        response.raise_for_status()
        self._tokens = self._parse_tokens(response.json())
        return self._tokens

    def validate(self, access_token: Optional[str] = None) -> bool:
        token = access_token or (self._tokens.access_token if self._tokens else None)
        if not token:
            return False

        response = self._session.post(
            self._build_url(self.VALIDATE_ENDPOINT),
            headers={'Authorization': f'Bearer {token}'},
            timeout=self._timeout,
            verify=self._verify_ssl,
        )
        if response.status_code != 200:
            return False

        try:
            return bool(response.json().get('valid'))
        except ValueError:
            return False

    def refresh(self, refresh_token: Optional[str] = None) -> TokenBundle:
        token = refresh_token or (self._tokens.refresh_token if self._tokens else None)
        if not token:
            raise RuntimeError('Missing refresh_token, unable to refresh tokens.')

        response = self._session.post(
            self._build_url(self.REFRESH_ENDPOINT),
            json={'refresh_token': token},
            timeout=self._timeout,
            verify=self._verify_ssl,
        )
        response.raise_for_status()
        self._tokens = self._parse_tokens(response.json())
        return self._tokens

    def logout(self, refresh_token: Optional[str] = None, access_token: Optional[str] = None) -> requests.Response:
        token = access_token or (self._tokens.access_token if self._tokens else None)
        refresh = refresh_token or (self._tokens.refresh_token if self._tokens else None)
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        body = {'refresh_token': refresh} if refresh else {}

        response = self._session.post(
            self._build_url(self.LOGOUT_ENDPOINT),
            json=body,
            headers=headers,
            timeout=self._timeout,
            verify=self._verify_ssl,
        )
        if response.status_code == 200:
            self._tokens = None
        return response

    def get_access_token(self) -> str:
        if self._tokens is None:
            return self.login().access_token

        if not self.validate(self._tokens.access_token):
            try:
                return self.refresh().access_token
            except Exception:
                return self.login().access_token

        return self._tokens.access_token

    def get_refresh_token(self) -> str:
        if self._tokens is None:
            return self.login().refresh_token or ''
        return self._tokens.refresh_token or ''

    def get_auth_header(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self.get_access_token()}'}
