import functools
import os
import uuid
from datetime import datetime
from pathlib import Path

import jwt
from jwt.exceptions import ExpiredSignatureError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from rest_framework_simplejwt.settings import api_settings

from core.token_blacklist import is_token_blacklisted

CERTS_DIR = Path(settings.BASE_DIR) / 'certs'
DEFAULT_PRIVATE_PEM = CERTS_DIR / 'private.pem'
DEFAULT_PUBLIC_PEM = CERTS_DIR / 'public.pem'


def _resolve_pem_path(env_name: str, default_path: Path) -> Path:
    configured = os.getenv(env_name)
    if configured:
        return Path(configured)
    return default_path


def _read_pem_bytes(path: Path) -> bytes:
    if not path.exists():
        raise FileNotFoundError(
            f'JWT PEM file not found at {path}. Run: ./scripts/generate_jwt_keys.sh'
        )
    return path.read_bytes()


@functools.lru_cache(maxsize=1)
def get_public_key():
    """
    Load RSA public key from local certs folder for JWT verification (decode).
    Override path with LOCAL_PUBLIC_PEM_FILE env var.
    """
    public_pem = _resolve_pem_path('LOCAL_PUBLIC_PEM_FILE', DEFAULT_PUBLIC_PEM)
    public_key = _read_pem_bytes(public_pem)
    return serialization.load_pem_public_key(public_key, backend=default_backend())


@functools.lru_cache(maxsize=1)
def get_private_key():
    """
    Load RSA private key from local certs folder for JWT signing (encode).
    Override path with LOCAL_PRIVATE_PEM_FILE env var.
    """
    private_pem = _resolve_pem_path('LOCAL_PRIVATE_PEM_FILE', DEFAULT_PRIVATE_PEM)
    private_key = _read_pem_bytes(private_pem)
    password = os.getenv('PEM_FILE_PWD', '')
    return serialization.load_pem_private_key(
        private_key,
        password=password.encode() if password else None,
        backend=default_backend(),
    )


def jwt_encode_handler(payload):
    """Sign JWT payload with private PEM (RS256)."""
    return jwt.encode(payload, get_private_key(), 'RS256')


def jwt_decode_handler(token, verify_exp=True):
    """Verify and decode JWT using public PEM (RS256)."""
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    if is_token_blacklisted(token):
        raise ExpiredSignatureError('Signature has expired')

    options = {'verify_exp': verify_exp}
    return jwt.decode(
        jwt=token,
        key=get_public_key(),
        algorithms=['RS256'],
        options=options,
        leeway=api_settings.LEEWAY,
        audience=api_settings.AUDIENCE,
        issuer=api_settings.ISSUER,
    )


def _utcnow():
    return datetime.utcnow()


def build_access_payload(user):
    lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
    now = _utcnow()
    return {
        'token_type': 'access',
        'exp': now + lifetime,
        'iat': now,
        'jti': str(uuid.uuid4()),
        'user_id': user.pk,
        'email': user.email,
        'role': user.access_level,
    }


def build_refresh_payload(user):
    lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    now = _utcnow()
    return {
        'token_type': 'refresh',
        'exp': now + lifetime,
        'iat': now,
        'jti': str(uuid.uuid4()),
        'user_id': user.pk,
    }


def generate_tokens_for_user(user):
    """Return access and refresh JWT strings for a user."""
    access = jwt_encode_handler(build_access_payload(user))
    refresh = jwt_encode_handler(build_refresh_payload(user))
    return access, refresh
