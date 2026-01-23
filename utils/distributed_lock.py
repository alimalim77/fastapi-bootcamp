"""
Distributed Lock using Redis
=============================
Prevents race conditions by ensuring only one process can execute
a critical section at a time, even across multiple servers.

Usage:
    with distributed_lock("verify:123"):
        # Only one request can be here at a time
        do_something()
"""
import redis
from contextlib import contextmanager
from fastapi import HTTPException
from utils.redis_client import get_redis_client


class LockAcquisitionError(Exception):
    """Raised when lock cannot be acquired."""
    pass


def acquire_lock(key: str, expire_seconds: int = 10) -> bool:
    """
    Try to acquire a lock.
    
    Args:
        key: Unique lock identifier (e.g., "verify:123")
        expire_seconds: Lock auto-expires after this time (prevents deadlocks)
    
    Returns:
        True if lock acquired, False if already locked
    """
    try:
        redis_client = get_redis_client()
        # SET if Not eXists (NX), with EXpiry (EX)
        result = redis_client.set(f"lock:{key}", "1", nx=True, ex=expire_seconds)
        print(f"[LOCK] Acquiring lock:{key} - {'SUCCESS' if result else 'BLOCKED'}")
        return result is True
    except redis.ConnectionError:
        # Redis down - allow operation (fail-open)
        print(f"[LOCK] Redis down, allowing lock:{key}")
        return True


def release_lock(key: str):
    """Release a lock."""
    try:
        redis_client = get_redis_client()
        redis_client.delete(f"lock:{key}")
    except redis.ConnectionError:
        pass  # Redis down - nothing to release


@contextmanager
def distributed_lock(key: str, expire_seconds: int = 10, wait: bool = False):
    """
    Context manager for distributed locking.
    
    Args:
        key: Unique lock identifier
        expire_seconds: Lock auto-expires after this time
        wait: If False, raise error immediately if locked
              If True, would wait (not implemented - raises immediately)
    
    Usage:
        with distributed_lock("verify:123"):
            # Critical section - only one at a time
            verify_otp(...)
    
    Raises:
        LockAcquisitionError: If lock cannot be acquired
    """
    if not acquire_lock(key, expire_seconds):
        raise LockAcquisitionError(f"Resource {key} is locked. Please try again.")
    
    try:
        yield
    finally:
        release_lock(key)


def require_lock(key_prefix: str, key_param: str = None):
    """
    Decorator for requiring a distributed lock.
    NOT USED - prefer the context manager for explicit control.
    """
    pass  # Context manager is clearer for this use case
