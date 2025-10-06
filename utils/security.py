import base64
import os
import secrets
import tempfile
from pathlib import Path
from typing import Optional

DEFAULT_SECRET_FILE = os.getenv("AUTH_SECRET_FILE", "./secrets/auth_secret.key")


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _atomic_write_text(path: Path, content: str) -> None:
    _ensure_parent_dir(path)
    dirpath = str(path.parent)

    with tempfile.NamedTemporaryFile("w", delete=False, dir=dirpath, encoding="utf-8") as tf:
        tf.write(content)
        tmp_name = tf.name
    os.replace(tmp_name, path)
    
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _generate_secret_str(num_bytes: int = 64) -> str:
    raw = secrets.token_bytes(num_bytes)
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def load_auth_secret(secret_file: Optional[str] = None) -> str:
    # Cross-service loader for AUTH_SECRET.
    # 1) ENV wins
    env_secret = os.getenv("AUTH_SECRET")
    if env_secret:
        return env_secret

    # 2) File
    file_path = Path(secret_file or DEFAULT_SECRET_FILE)
    if file_path.exists():
        return file_path.read_text(encoding="utf-8").strip()

    # 3) Generate once and persist
    secret = _generate_secret_str(64)
    _atomic_write_text(file_path, secret)
    return secret
