# Rate Limiting

Redis-based rate limiting to protect API endpoints from abuse.

---

## Overview

Rate limiting prevents brute force attacks and API abuse by limiting how many requests a client can make within a time window.

```
Request → Rate Limiter → Redis Check → Allow/Deny (429)
```

---

## Configuration

### Environment Variable

Add to `.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

### Install Redis (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
redis-cli ping  # Should return PONG
```

---

## Endpoint Limits

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `/register` | 3/hour | Prevent spam accounts |
| `/verify-otp` | 5/minute | Block OTP brute force |
| `/login` | 5/minute | Block password guessing |
| `/refresh` | 10/minute | Normal refresh usage |

---

## Implementation

### Redis Client

**File**: `utils/redis_client.py`

```python
@lru_cache()
def get_redis_client() -> redis.Redis:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url, decode_responses=True)
```

Uses connection pooling via `lru_cache` singleton.

### Rate Limiter Middleware

**File**: `middlewares/rate_limiter.py`

```python
from middlewares.rate_limiter import rate_limit

@router.post("/login")
@rate_limit("5/minute")
async def login(request: Request, ...):
    ...
```

### Rate Format

| Format | Period |
|--------|--------|
| `5/second` | 1 second |
| `5/minute` | 60 seconds |
| `10/hour` | 3600 seconds |
| `100/day` | 86400 seconds |

---

## How It Works

Uses **fixed window** algorithm:

```python
key = f"rate:{endpoint}:{client_ip}"
count = redis.incr(key)
if count == 1:
    redis.expire(key, window_seconds)
if count > limit:
    raise HTTPException(429, "Rate limit exceeded")
```

**Benefits**:
- Simple to implement
- Atomic Redis operations (thread-safe)
- Auto-expiring keys (no cleanup needed)

---

## Error Response

When rate limited, returns:

```json
{
    "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

**HTTP Status**: `429 Too Many Requests`

---

## Fail-Open Behavior

If Redis is unavailable, requests are **allowed** (fail-open):

```python
except redis.ConnectionError:
    return True  # Allow request if Redis down
```

This prevents Redis outages from blocking the entire API.

---

## Testing Rate Limits

```bash
# Hit login 6 times quickly
for i in {1..6}; do
  echo "Request $i:"
  curl -s -X POST http://localhost:8000/api/v1/users/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' | jq -r '.detail'
done

# Expected: Request 6 returns "Rate limit exceeded..."
```

### View Redis Keys

```bash
redis-cli keys "rate:*"
redis-cli get "rate:login_for_access_token:127.0.0.1"
```

---

## Custom Rate Limits

Apply to any endpoint:

```python
from middlewares.rate_limiter import rate_limit

@router.post("/sensitive-action")
@rate_limit("1/hour")
async def sensitive_action(request: Request):
    ...
```

---

[← Back to Index](./README.md) | [Previous: Configuration](./14-configuration.md)
