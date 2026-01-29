# Prometheus & Grafana Monitoring Guide

## What is Monitoring?

**Monitoring** is like having a dashboard for your car - it tells you how fast you're going, how much fuel you have, and warns you if something is wrong. For applications, monitoring tells you:

- How many requests are being processed?
- How fast is the system responding?
- Are there any errors?
- Is the system overloaded?

---

## The Monitoring Stack

### Prometheus
**What it is:** A time-series database that collects and stores metrics.

**Analogy:** Think of Prometheus as a **data collector** that visits your application every 15 seconds and writes down important numbers (like a census worker).

### Grafana
**What it is:** A visualization tool that creates beautiful dashboards from Prometheus data.

**Analogy:** Think of Grafana as an **artist** that takes the numbers collected by Prometheus and turns them into graphs and charts you can understand.

```
┌─────────────┐     scrapes every     ┌─────────────┐     queries     ┌─────────────┐
│  Your App   │ ◄──── 15 seconds ──── │ Prometheus  │ ◄───────────── │   Grafana   │
│  /metrics   │                       │  (Database) │                │ (Dashboard) │
└─────────────┘                       └─────────────┘                └─────────────┘
```

---

## How It Works in This Project

### Step 1: Your App Exposes Metrics

Your application exposes a `/metrics` endpoint that returns data in a special format:

```
# HELP email_attempts_total Total number of email send attempts
# TYPE email_attempts_total counter
email_attempts_total{status="success"} 15.0
email_attempts_total{status="failure"} 7.0

# HELP dlq_messages_total Total number of messages sent to Dead Letter Queue
# TYPE dlq_messages_total counter
dlq_messages_total{topic="email-dlq"} 5.0
```

**Where this is defined:**

| File | Purpose |
|------|---------|
| `utils/metrics.py` | Defines the metrics (counters, histograms) |
| `index.py` (line 33) | Exposes `/metrics` for FastAPI app |
| `workers/email_worker.py` (line 91) | Exposes `/metrics` for email worker |

---

### Step 2: Prometheus Scrapes the Metrics

Prometheus is configured to "scrape" (fetch) metrics from your services every 15 seconds.

**Configuration (in `docker-compose.yml`):**

```yaml
prometheus:
  entrypoint:
    - /bin/sh
    - -c
    - |
      cat > /etc/prometheus/prometheus.yml << 'EOF'
      global:
        scrape_interval: 15s        # How often to collect metrics
      
      scrape_configs:
        - job_name: 'fastapi'       # Name for this target
          static_configs:
            - targets: ['app:8000'] # Where to scrape
          metrics_path: '/metrics'  # The endpoint path
        
        - job_name: 'email_worker'
          static_configs:
            - targets: ['email_worker:8001']
        
        - job_name: 'kafka_exporter'
          static_configs:
            - targets: ['kafka-exporter:9308']
      EOF
```

**What each field means:**

| Field | Meaning |
|-------|---------|
| `scrape_interval: 15s` | Collect metrics every 15 seconds |
| `job_name` | A label to identify this target in queries |
| `targets` | The hostname:port to scrape |
| `metrics_path` | The URL path (default is `/metrics`) |

---

### Step 3: Grafana Visualizes the Data

Grafana connects to Prometheus and lets you create dashboards with graphs, charts, and alerts.

**Access:** http://localhost:3000
**Login:** admin / admin

---

## Types of Metrics

### 1. Counter
A value that only goes up (like an odometer in a car).

```python
from prometheus_client import Counter

email_attempts_total = Counter(
    'email_attempts_total',           # Metric name
    'Total number of email attempts', # Description
    ['status']                        # Labels (success/failure)
)

# Usage:
email_attempts_total.labels(status="success").inc()  # Add 1
```

**Good for:**
- Total requests processed
- Total errors occurred
- Total emails sent

---

### 2. Histogram
Measures the distribution of values (like response times).

```python
from prometheus_client import Histogram

email_processing_seconds = Histogram(
    'email_processing_seconds',
    'Time spent processing email tasks',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]  # Time buckets
)

# Usage:
email_processing_seconds.observe(2.5)  # Record a 2.5 second duration
```

**Good for:**
- Response times
- Processing durations
- Request sizes

**Buckets explained:**
| Bucket | Meaning |
|--------|---------|
| `le="0.1"` | Requests faster than 0.1 seconds |
| `le="1.0"` | Requests faster than 1 second |
| `le="+Inf"` | All requests (total) |

---

### 3. Gauge
A value that can go up or down (like a thermometer).

```python
from prometheus_client import Gauge

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# Usage:
active_connections.set(42)   # Set to 42
active_connections.inc()     # Add 1
active_connections.dec()     # Subtract 1
```

**Good for:**
- Current queue size
- Active users
- Memory usage

---

## Metrics in This Project

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `email_attempts_total` | Counter | `status` | Total email send attempts |
| `email_processing_seconds` | Histogram | - | Email processing duration |
| `dlq_messages_total` | Counter | `topic` | Messages sent to DLQ |

---

## Common Grafana Queries (PromQL)

### Total Successful Emails
```promql
email_attempts_total{status="success"}
```

### Total Failed Emails
```promql
email_attempts_total{status="failure"}
```

### Success Rate (percentage)
```promql
email_attempts_total{status="success"} / 
(email_attempts_total{status="success"} + email_attempts_total{status="failure"}) * 100
```

### Emails per Minute
```promql
rate(email_attempts_total[1m]) * 60
```

### Average Processing Time
```promql
rate(email_processing_seconds_sum[5m]) / rate(email_processing_seconds_count[5m])
```

### DLQ Messages
```promql
dlq_messages_total{topic="email-dlq"}
```

---

## Setting Up Grafana Dashboard

### 1. Add Prometheus Data Source (First Time Only)
1. Go to http://localhost:3000
2. Login: admin / admin
3. Go to **Connections** → **Data Sources**
4. Click **Add data source**
5. Select **Prometheus**
6. URL: `http://prometheus:9090`
7. Click **Save & Test**

### 2. Create a Panel
1. Go to **Dashboards** → **New Dashboard**
2. Click **Add visualization**
3. Select **prometheus** data source
4. Enter your query (e.g., `email_attempts_total`)
5. Click **Run query**
6. Choose visualization type (Graph, Stat, etc.)
7. Click **Apply**

### 3. Useful Visualizations

| Panel Type | Best For |
|------------|----------|
| **Time Series** | Showing trends over time |
| **Stat** | Single big number (total count) |
| **Gauge** | Showing percentage or ratio |
| **Bar Chart** | Comparing categories |
| **Table** | Detailed breakdown |

---

## Accessing the Services

| Service | URL | Purpose |
|---------|-----|---------|
| **FastAPI Metrics** | http://localhost:8000/metrics | Raw metrics from app |
| **Email Worker Metrics** | http://localhost:8002/metrics | Raw metrics from worker |
| **Prometheus** | http://localhost:9095 | Query and explore metrics |
| **Prometheus Targets** | http://localhost:9095/targets | Check if scraping works |
| **Grafana** | http://localhost:3000 | Create dashboards |

---

## Troubleshooting

### Target Shows "DOWN" in Prometheus

**Check if service is running:**
```bash
docker ps | grep <service_name>
```

**Check if metrics endpoint works:**
```bash
curl http://localhost:8000/metrics  # For FastAPI
curl http://localhost:8002/metrics  # For Email Worker
```

**Common causes:**
- Service isn't running
- Wrong port in configuration
- Firewall blocking connection
- `/metrics` endpoint not configured

---

### Grafana Shows "No Data"

1. **Check time range** - Select "Last 15 minutes" or "Last 1 hour"
2. **Check data source** - Make sure Prometheus is selected
3. **Check query syntax** - Run in Prometheus first to verify
4. **Check if metric exists** - Go to Prometheus → Graph → type metric name

---

## Docker Compose Services

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9095:9090"    # Access on localhost:9095
    # Configuration is embedded in entrypoint

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"    # Access on localhost:3000
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
    depends_on:
      - prometheus
```

---

## Best Practices

1. **Name metrics clearly** - Use format: `<app>_<what>_<unit>` (e.g., `email_processing_seconds`)

2. **Use labels wisely** - Good labels: `status`, `endpoint`, `method`. Bad labels: `user_id`, `timestamp`

3. **Monitor the monitors** - Check Prometheus targets page regularly

4. **Set up alerts** - Don't just watch dashboards, get notified of problems

5. **Keep dashboards simple** - 3-5 panels per dashboard, not 50

---

## Summary

| Component | Role | URL |
|-----------|------|-----|
| Your App | Exposes `/metrics` with current stats | :8000/metrics |
| Prometheus | Collects metrics every 15s, stores them | :9095 |
| Grafana | Visualizes metrics with dashboards | :3000 |

**The cycle:**
1. Your app updates metrics (counters, histograms)
2. Prometheus scrapes them every 15 seconds
3. Grafana queries Prometheus and displays graphs
4. You see pretty dashboards! 📊
