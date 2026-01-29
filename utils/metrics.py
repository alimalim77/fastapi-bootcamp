"""
Prometheus Metrics for Kafka Email Queue
=========================================
Centralized metrics for monitoring DLQ and email processing.
"""
from prometheus_client import Counter, Histogram, REGISTRY

# DLQ Counter - tracks messages sent to Dead Letter Queue
dlq_messages_total = Counter(
    'dlq_messages_total',
    'Total number of messages sent to Dead Letter Queue',
    ['topic']
)

# Email attempt counter - tracks success/failure
email_attempts_total = Counter(
    'email_attempts_total',
    'Total number of email send attempts',
    ['status']  # 'success' or 'failure'
)

# Email processing time histogram
email_processing_seconds = Histogram(
    'email_processing_seconds',
    'Time spent processing email tasks',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)


def increment_dlq_counter(topic: str = "email-dlq"):
    """Increment DLQ counter when a message is sent to DLQ."""
    dlq_messages_total.labels(topic=topic).inc()


def increment_email_attempt(success: bool):
    """Increment email attempt counter."""
    status = "success" if success else "failure"
    email_attempts_total.labels(status=status).inc()


def observe_email_processing_time(duration_seconds: float):
    """Record email processing duration."""
    email_processing_seconds.observe(duration_seconds)
