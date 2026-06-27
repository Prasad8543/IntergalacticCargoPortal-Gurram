import hashlib
from datetime import datetime, timezone

import jwt
from django.conf import settings

from core.utils import get_cache

BLACKLIST_CACHE_PREFIX = 'jwt:blacklist:'


def _normalize_token(token):
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token


def _blacklist_cache_key(token):
    normalized = _normalize_token(token)
    digest = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    return f'{BLACKLIST_CACHE_PREFIX}{digest}'


def is_token_blacklisted(token):
    return get_cache().get(_blacklist_cache_key(token)) is not None


def _blacklist_timeout_seconds(token):
    normalized = _normalize_token(token)
    default_ttl = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    try:
        payload = jwt.decode(
            normalized,
            options={'verify_signature': False, 'verify_exp': False},
            algorithms=['RS256'],
        )
    except jwt.PyJWTError:
        return default_ttl

    exp = payload.get('exp')
    if not exp:
        return default_ttl

    remaining = int(exp - datetime.now(timezone.utc).timestamp())
    return max(remaining, 1)


def blacklist_token(token):
    timeout = _blacklist_timeout_seconds(token)
    get_cache().set(_blacklist_cache_key(token), True, timeout=timeout)
