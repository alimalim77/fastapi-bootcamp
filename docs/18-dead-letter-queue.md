# Dead Letter Queue (DLQ) Guide

## What is a Dead Letter Queue?

A **Dead Letter Queue (DLQ)** is a special queue where messages that can't be processed successfully are sent for later analysis. Think of it like a "lost and found" box for failed messages.

### Real-World Analogy
Imagine a post office:
- **Normal Queue** = Regular mail delivery
- **DLQ** = Undeliverable mail pile (wrong address, damaged, etc.)

Instead of losing these letters, they're set aside so someone can investigate why delivery failed.

---

## Why Do We Need a DLQ?

Without a DLQ, failed messages would either:
1. **Be lost forever** - Bad! You'd never know something failed
2. **Retry infinitely** - Bad! Wastes resources, blocks other messages
3. **Crash the system** - Bad! One bad message breaks everything

With a DLQ:
- ✅ Failed messages are safely stored
- ✅ System continues processing other messages
- ✅ You can investigate and fix issues later
- ✅ You can replay messages after fixing the problem

---

## How DLQ Works in This Project

### The Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           HAPPY PATH (Success)                         │
└─────────────────────────────────────────────────────────────────────────┘

User Registration → Kafka Queue → Email Worker → ✅ Email Sent Successfully
                    (email-queue)     │
                                      └── Records: email_attempts_total{status="success"}


┌─────────────────────────────────────────────────────────────────────────┐
│                           SAD PATH (Failure)                            │
└─────────────────────────────────────────────────────────────────────────┘

User Registration → Kafka Queue → Email Worker → ❌ Attempt 1 FAILED
                    (email-queue)     │              (wait 1 second)
                                      │
                                      ├── ❌ Attempt 2 FAILED
                                      │      (wait 2 seconds)
                                      │
                                      ├── ❌ Attempt 3 FAILED (final)
                                      │
                                      └── Message sent to DLQ (email-dlq)
                                          Records: dlq_messages_total
                                          Records: email_attempts_total{status="failure"}
```

---

## Code Implementation

### 1. Retry Logic with Exponential Backoff

**File:** `workers/email_worker.py`

```python
MAX_RETRIES = 3
BACKOFF_BASE = 1  # Base delay in seconds

def process_email_with_retry(data: dict) -> bool:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            send_otp_email(to_email, otp)
            print(f"✓ Email sent successfully on attempt {attempt}!")
            increment_email_attempt(success=True)  # Record success
            return True
            
        except Exception as e:
            print(f"✗ Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            
            if attempt < MAX_RETRIES:
                delay = BACKOFF_BASE * (2 ** (attempt - 1))  # 1s, 2s, 4s
                time.sleep(delay)
    
    # All retries failed - send to DLQ
    send_to_dlq(data, str(last_error), MAX_RETRIES)
    increment_email_attempt(success=False)  # Record failure
    return False
```

**Exponential Backoff Explained:**
| Attempt | Wait Time | Why? |
|---------|-----------|------|
| 1 | 0s (immediate) | Try right away |
| 2 | 1s | Quick retry for transient errors |
| 3 | 2s | Longer wait, maybe server is recovering |
| Failed | → DLQ | Give up, save for investigation |

---

### 2. Sending to DLQ

**File:** `utils/kafka_producer.py`

```python
def send_to_dlq(original_message: dict, error_reason: str, retry_count: int):
    """
    Send a failed message to the Dead Letter Queue for later investigation.
    """
    dlq_message = {
        "original_message": original_message,
        "error_reason": error_reason,
        "retry_count": retry_count,
        "failed_at": datetime.now().isoformat(),
        "worker_id": "email_worker"
    }
    
    producer.send("email-dlq", value=dlq_message)  # Send to DLQ topic
    increment_dlq_counter(topic="email-dlq")       # Record in metrics
    print(f"Message sent to DLQ: {original_message.get('to')}")
```

**What's stored in DLQ:**
| Field | Purpose |
|-------|---------|
| `original_message` | The email data that failed |
| `error_reason` | Why it failed (exception message) |
| `retry_count` | How many times we tried |
| `failed_at` | Timestamp for debugging |
| `worker_id` | Which worker processed it |

---

### 3. Tracking DLQ Metrics

**File:** `utils/metrics.py`

```python
from prometheus_client import Counter

# DLQ Counter - tracks messages sent to Dead Letter Queue
dlq_messages_total = Counter(
    'dlq_messages_total',
    'Total number of messages sent to Dead Letter Queue',
    ['topic']  # Label to identify which DLQ
)

def increment_dlq_counter(topic: str = "email-dlq"):
    """Increment DLQ counter when a message is sent to DLQ."""
    dlq_messages_total.labels(topic=topic).inc()
```

---

## Monitoring DLQ in Grafana

### Query to See DLQ Messages
```promql
dlq_messages_total{topic="email-dlq"}
```

### Alert Idea (if DLQ grows too fast)
```promql
rate(dlq_messages_total[5m]) > 0.1  # More than 0.1 messages/second = problem!
```

---

## Common DLQ Scenarios

| Scenario | What Happens | DLQ Message Contains |
|----------|--------------|----------------------|
| Invalid email address | SMTP rejects it | `error_reason: "No such user"` |
| SMTP server down | Connection refused | `error_reason: "Connection refused"` |
| Network timeout | Takes too long | `error_reason: "Connection timed out"` |
| Rate limited | Too many emails | `error_reason: "Too many requests"` |

---

## How to Handle DLQ Messages

### Option 1: Manual Review
```bash
# View messages in DLQ topic
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic email-dlq \
  --from-beginning
```

### Option 2: Automated Retry (Future Enhancement)
Create a separate worker that:
1. Reads from `email-dlq`
2. Waits some time (hours/days)
3. Retries sending the email
4. If still failing, alert a human

### Option 3: Alert and Investigate
Set up Grafana alerts when `dlq_messages_total` increases, then investigate root cause.

---

## Best Practices

1. **Always have a DLQ** - Never silently drop failed messages
2. **Log everything** - Include timestamps, error reasons, retry counts
3. **Monitor DLQ size** - Growing DLQ = something is wrong
4. **Set retention** - Don't keep DLQ messages forever (disk fills up)
5. **Alert on spikes** - Sudden increase in DLQ = investigate immediately

---

## Summary

| Concept | In This Project |
|---------|-----------------|
| Main Queue | `email-queue` (Kafka topic) |
| Dead Letter Queue | `email-dlq` (Kafka topic) |
| Max Retries | 3 attempts |
| Backoff Strategy | Exponential (1s, 2s, 4s) |
| Metrics | `dlq_messages_total`, `email_attempts_total` |
| Monitoring | Prometheus + Grafana |
