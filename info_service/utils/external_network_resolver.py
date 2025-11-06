from ipaddress import ip_address
from typing import ClassVar, Optional
from urllib.request import urlopen

from info_service.models.external.external_network_info import ExternalNetworkInfo


class ExternalNetworkResolver:
    """
    Static utility for resolving external network information via public IP services.
    """

    _ENDPOINTS: ClassVar[list] = [
        'https://api.ipify.org',
        'https://checkip.amazonaws.com',
        'https://ifconfig.me/ip',
        'https://icanhazip.com'
    ]

    @classmethod
    def _get_public_ip_address(cls) -> Optional[str]:
        """
        Fetch the public IP address from a list of known endpoints.
        """
        for url in cls._ENDPOINTS:
            try:
                with urlopen(url, timeout=4) as resp:
                    text = resp.read().decode('utf-8').strip()
                    # Validate the returned value is a valid IP (IPv4 or IPv6)
                    ip_address(text)
                    return text
            except Exception:
                continue
        return None
    
    @classmethod
    def get_external_network_info(cls) -> Optional[ExternalNetworkInfo]:
        """
        Return an ExternalNetworkInfo object with the public IP address.
        """
        addr = cls._get_public_ip_address()
        if not addr:
            return None
        return ExternalNetworkInfo(address=addr)