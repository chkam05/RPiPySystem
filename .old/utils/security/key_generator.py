import base64
import secrets


class KeyGenerator:
    """Static utility class for generating secure random URL-safe secret strings."""

    def __new__(cls, *args, **kwargs):
        """Prevent instantiation of this static utility class."""
        raise TypeError(f'{cls.__name__} is a static class and cannot be instantiated.')
    
    @staticmethod
    def generate_secret_str(num_bytes: int = 64) -> str:
        """
        Returns a base64 urlsafe without '=' with entropy ~ num_bytes*8 bits.
        Ideal for AUTH_SECRET / cookies / session keys.
        """
        raw = secrets.token_bytes(num_bytes)
        return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')