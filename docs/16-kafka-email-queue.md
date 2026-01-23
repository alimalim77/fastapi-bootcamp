# Kafka Email Queue

Async email sending using Apache Kafka message queue.

---

## Overview

Instead of blocking the API while sending emails, messages are published to Kafka and processed by a separate worker.

```
API (instant response) → Kafka Queue → Email Worker → Gmail
```

**Benefit**: Registration API responds in ~50ms instead of 3-5 seconds.

---

## Setup

### 1. Start Kafka

```bash
docker compose -f docker-compose.kafka.yml up -d
```

### 2. Start Email Worker (separate terminal)

```bash
source .venv/bin/activate
python workers/email_worker.py
```

### 3. Start FastAPI

```bash
uvicorn index:app --reload
```

---

## Configuration

**.env**:
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9094
```

---

## Architecture

| Component | File | Purpose |
|-----------|------|---------|
| Producer | `utils/kafka_producer.py` | Sends email tasks to Kafka |
| Consumer | `workers/email_worker.py` | Reads tasks and sends emails |
| Topic | `email-queue` | Kafka topic for email messages |

---

## Fallback Behavior

If Kafka is unavailable, the API automatically falls back to synchronous email sending.

---

[← Back to Index](./README.md) | [Previous: Rate Limiting](./15-rate-limiting.md)
