# Distributed Locks

Redis-based distributed locking to prevent race conditions.

---

## Use Cases

| Endpoint | Lock Key | Prevents |
|----------|----------|----------|
| `/register` | `register:{email}` | Duplicate registrations |
| `/verify-otp` | `verify:{pending_id}` | Same OTP used twice |

---

## How It Works

```python
with distributed_lock("verify:123", expire_seconds=10):
    # Only one request at a time can be here
    verify_otp(...)
```

- Lock auto-expires in 10 seconds (prevents deadlocks)
- Returns HTTP 429 if lock busy
- If Redis down: proceeds without lock (fail-open)

---

## Testing

```bash
# Send two requests simultaneously
curl -X POST http://localhost:8000/api/v1/users/verify-otp ... &
curl -X POST http://localhost:8000/api/v1/users/verify-otp ... &

# Second request should get 429: "Verification in progress"
```

---

[← Back to Index](./README.md) | [Previous: Kafka Email Queue](./16-kafka-email-queue.md)
