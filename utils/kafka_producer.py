"""
Kafka Producer Utility
=======================
Handles sending messages to Kafka queues.
"""
import os
import json
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
from prometheus_client import Counter
from utils.metrics import increment_dlq_counter


# Topic names
EMAIL_QUEUE_TOPIC = "email-queue"
EMAIL_DLQ_TOPIC = "email-dlq"


# Prometheus Metrics
KAFKA_MESSAGES_PRODUCED_TOTAL = Counter(
    'kafka_messages_produced_total',
    'Total number of Kafka messages produced',
    ['topic', 'status']
)

KAFKA_DLQ_MESSAGES_TOTAL = Counter(
    "kafka_dl_messages_total",
    "Total number of messages sent to Dead Letter Queue",
    ["status"]
)

_producer = None

def get_kafka_producer():
    """Get or create singleton Kafka producer."""
    global _producer
    if _producer is None:
        try:
            bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
            print(f"Connecting to Kafka producer at {bootstrap_servers}...")
            _producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3    # Retry sending if fails
            )
            print("Kafka producer connected!")
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")
            return None
    return _producer

def send_email_task(to_email: str, otp: str, retry_count: int = 0) -> bool:
    """
    Send an email task to the Kafka queue.
    
    Args:
        to_email: Data to send
        otp: OTP code
        retry_count: Number of times this has been retried (default 0)
    
    Returns:
        bool: True if sent (or queued), False if failed
    """
    producer = get_kafka_producer()
    if not producer:
        return False
    
    try:
        task = {
            "type": "send_otp",
            "to": to_email,
            "otp": otp,
            "retry_count": retry_count
        }
        
        # Send to Kafka topic "email-queue"
        future = producer.send(EMAIL_QUEUE_TOPIC, message)
        
        # Wait for send to complete (with timeout)
        future.get(timeout=10)
        
        
        print(f"Email task queued for {to_email}")
        KAFKA_MESSAGES_PRODUCED_TOTAL.labels(topic='email-queue', status='success').inc()
        return True
        
    except Exception as e:
        print(f"Failed to send task to Kafka: {e}")
        KAFKA_MESSAGES_PRODUCED_TOTAL.labels(topic='email-queue', status='failed').inc()
        return False

def send_to_dlq(task_data: dict, error_reason: str) -> bool:
    """
    Send a failed task to the Dead Letter Queue (DLQ).
    """
    producer = get_kafka_producer()
    if not producer:
        return False
        
    try:
        dlq_data = {
            "original_task": task_data,
            "error": error_reason,
            "failed_at": str(os.getenv("HOSTNAME", "unknown"))
        }
        producer.send('email-dlq', dlq_data).get(timeout=10)
        producer.send('email-dlq', dlq_data).get(timeout=10)
        print(f"Task sent to DLQ: {task_data}")
        KAFKA_DLQ_MESSAGES_TOTAL.labels(status='success').inc()
        return True
    except Exception as e:
        print(f"Failed to send to DLQ: {e}")
        KAFKA_DLQ_MESSAGES_TOTAL.labels(status='failed').inc()
        return False
    
    finally:
        producer.close()


def send_to_dlq(original_message: dict, error: str, retry_count: int) -> bool:
    """
    Send a failed message to the Dead Letter Queue.
    
    Args:
        original_message: The original message that failed
        error: Error message describing why it failed
        retry_count: Number of retries attempted
    
    Returns:
        True if sent to DLQ successfully, False otherwise
    """
    producer = get_kafka_producer()
    
    if producer is None:
        print("Cannot send to DLQ: Kafka not available")
        return False
    
    try:
        dlq_message = {
            "original_message": original_message,
            "error": str(error),
            "retry_count": retry_count,
            "failed_at": datetime.utcnow().isoformat() + "Z",
            "source_topic": EMAIL_QUEUE_TOPIC
        }
        
        future = producer.send(EMAIL_DLQ_TOPIC, dlq_message)
        future.get(timeout=10)
        
        # Increment Prometheus DLQ counter
        increment_dlq_counter(EMAIL_DLQ_TOPIC)
        
        print(f"Message sent to DLQ: {original_message.get('to', 'unknown')}")
        return True
        
    except KafkaError as e:
        print(f"Failed to send to DLQ: {e}")
        return False
    
    finally:
        producer.close()

