"""
Redis client singleton with connection pooling.
Used for rate limiting and session management.
"""
import os
import redis
from functools import lru_cache


@lru_cache()
def get_redis_client() -> redis.Redis:
    """
    Get Redis client instance (singleton).
    Uses connection pooling for efficiency.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url, decode_responses=True)


def check_redis_connection() -> bool:
    """Check if Redis is available."""
    try:
        client = get_redis_client()
        return client.ping()
    except redis.ConnectionError:
        return False
