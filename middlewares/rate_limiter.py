"""
Rate limiting middleware using Redis.
Provides decorator-based rate limiting for FastAPI endpoints.
"""
from functools import wraps
from fastapi import HTTPException, Request
from utils.redis_client import get_redis_client
import redis


class RateLimiter:
    """
    Rate limiter using Redis sliding window algorithm.
    
    Usage:
        limiter = RateLimiter()
        
        @router.post("/login")
        @limiter.limit("5/minute", key_func=lambda r: r.client.host)
        async def login(request: Request):
            ...
    """
    
    def __init__(self):
        self.redis = get_redis_client()
    
    def limit(self, rate: str, key_func=None):
        """
        Rate limit decorator.
        
        Args:
            rate: Rate limit string like "5/minute", "10/hour", "3/day"
            key_func: Function to extract key from request (default: IP address)
        """
        limit, period = self._parse_rate(rate)
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Find request object in args or kwargs
                request = kwargs.get("request") or next(
                    (arg for arg in args if isinstance(arg, Request)), None
                )
                
                if request is None:
                    # If no request found, skip rate limiting
                    return await func(*args, **kwargs)
                
                # Generate key
                if key_func:
                    identifier = key_func(request)
                else:
                    identifier = request.client.host if request.client else "unknown"
                
                key = f"rate:{func.__name__}:{identifier}"
                
                # Check and increment counter
                if not self._is_allowed(key, limit, period):
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Try again in {period} seconds."
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _parse_rate(self, rate: str) -> tuple[int, int]:
        """Parse rate string like '5/minute' to (limit, seconds)."""
        parts = rate.split("/")
        limit = int(parts[0])
        
        period_map = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }
        
        period = period_map.get(parts[1], 60)
        return limit, period
    
    def _is_allowed(self, key: str, limit: int, period: int) -> bool:
        """
        Check if request is within rate limit using fixed window.
        Returns True if allowed, False if rate limited.
        """
        try:
            current = self.redis.get(key)
            
            if current is None:
                # First request in window
                self.redis.setex(key, period, 1)
                return True
            
            if int(current) >= limit:
                return False
            
            # Increment counter
            self.redis.incr(key)
            return True
            
        except redis.ConnectionError:
            # If Redis is down, allow request (fail open)
            return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(rate: str, key_func=None):
    """
    Convenience function for rate limiting.
    
    Usage:
        @router.post("/login")
        @rate_limit("5/minute")
        async def login(request: Request):
            ...
    """
    return rate_limiter.limit(rate, key_func)
