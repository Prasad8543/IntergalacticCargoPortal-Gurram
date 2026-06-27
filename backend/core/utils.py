import logging

import redis
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

_redis_client = None
_cache_initialized = False


def init_redis_cache() -> None:
    """Initialize Django cache backend and Redis client connection pool."""
    global _redis_client, _cache_initialized

    if _cache_initialized:
        return

    redis_url = settings.REDIS_URL

    try:
        _redis_client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
        )
        _redis_client.ping()
        cache.set('core:redis:healthcheck', 'ok', timeout=60)
        logger.info('Redis cache initialized at %s', redis_url)
    except (redis.RedisError, Exception) as exc:
        _redis_client = None
        logger.warning('Redis unavailable (%s). Cache operations may use fallback behavior.', exc)

    _cache_initialized = True


def get_redis_client():
    """Return the shared Redis client, initializing cache if needed."""
    if not _cache_initialized:
        init_redis_cache()
    return _redis_client


def get_cache():
    """Return Django cache interface backed by Redis when available."""
    if not _cache_initialized:
        init_redis_cache()
    return cache
