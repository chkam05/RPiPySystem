from typing import Any, ClassVar, Dict, Optional
from urllib.parse import urljoin

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from tests.common.models.token_bundle import TokenBundle
from tests.common.models.user_info import UserInfo


class Authenticator:
    LOGIN_ENDPOINT: ClassVar[str] = '/sessions/login'
    REFRESH_ENDPOINT: ClassVar[str] = '/sessions/refresh'
    LOGOUT_ENDPOINT: ClassVar[str] = '/sessions/logout'
    VALIDATE_ENDPOINT: ClassVar[str] = '/sessions/validate'

    def __init__(
            self,
            base_address: str,
            username: str,
            password: str
    ) -> None:
        self._base_address = base_address.rstrip('/')
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._tokens: Optional[TokenBundle] = None

    def _parse_tokens(self, data: Dict[str, Any]) -> TokenBundle:
        access = data.get('access_token')
        if not access:
            raise ValueError('Missing "access_token" in API response.')
        refresh = data.get('refresh_token')
        token_type = data.get('token_type', 'Bearer')
        return TokenBundle(access, refresh, token_type)

    def _is_token_valid(self) -> bool:
        """
        Checks token validity via endpoint /sessions/validate.
        """
        if not self._tokens or not self._tokens.access_token:
            return False

        url = urljoin(self._base_address + '/', self.VALIDATE_ENDPOINT.lstrip('/'))
        headers = {'Authorization': f'Bearer {self._tokens.access_token}'}

        try:
            resp = self._session.post(url, headers=headers, verify=False)
            if resp.status_code != 200:
                return False
            data = resp.json()
            return bool(data.get('valid', False))
        except Exception:
            return False

    def _login(self) -> None:
        """
        Login - Gets access_token and refresh_token.
        """
        url = urljoin(self._base_address + '/', self.LOGIN_ENDPOINT.lstrip('/'))
        resp = self._session.post(
            url,
            json={'name': self._username, 'password': self._password},
            verify=False,
        )
        resp.raise_for_status()
        data = resp.json()
        self._tokens = self._parse_tokens(data)
    
    def _refresh(self) -> None:
        """
        Refreshing the token via refresh_token.
        """
        if not self._tokens or not self._tokens.refresh_token:
            raise RuntimeError('Missing "refresh_token", unable to refresh token.')
        
        url = urljoin(self._base_address + '/', self.REFRESH_ENDPOINT.lstrip('/'))
        resp = self._session.post(
            url,
            json={'refresh_token': self._tokens.refresh_token},
            verify=False,
        )
        resp.raise_for_status()
        data = resp.json()
        self._tokens = self._parse_tokens(data)
    
    def get_access_token(self) -> str:
        """
        Returns valid access_token, automatically logging in or refreshing.
        """
        # Pierwsze użycie → logowanie
        if self._tokens is None:
            self._login()
            return self._tokens.access_token  # type: ignore[union-attr]

        # Sprawdź ważność przez /sessions/validate
        if not self._is_token_valid():
            try:
                self._refresh()
            except Exception:
                self._login()

        return self._tokens.access_token  # type: ignore[union-attr]
    
    def get_auth_header(self) -> Dict[str, str]:
        """
        Returns the Authorization header.
        """
        token = self.get_access_token()
        return {'Authorization': f'Bearer {token}'}
