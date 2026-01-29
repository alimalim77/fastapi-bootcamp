"""
Kafka Producer for Email Queue
==============================
Sends email tasks to Kafka for async processing.
The email worker (consumer) will pick up these messages and send the actual emails.
"""
import os
import json
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
from utils.metrics import increment_dlq_counter


# Topic names
EMAIL_QUEUE_TOPIC = "email-queue"
EMAIL_DLQ_TOPIC = "email-dlq"



def get_kafka_producer():
    """
    Create and return a Kafka producer.
    Returns None if Kafka is not available.
    """
    try:
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            # Wait for message to be acknowledged
            acks='all',
            # Retry on failure
            retries=3
        )
        return producer
    except KafkaError as e:
        print(f"Failed to connect to Kafka: {e}")
        return None


def send_email_task(to_email: str, otp: str) -> bool:
    """
    Send an email task to Kafka queue.
    
    Args:
        to_email: Recipient email address
        otp: The OTP code to send
    
    Returns:
        True if message was sent successfully, False otherwise
    
    Example:
        send_email_task("user@example.com", "123456")
    """
    producer = get_kafka_producer()
    
    if producer is None:
        print("Kafka not available, falling back to sync email")
        return False
    
    try:
        # Create the message
        message = {
            "to": to_email,
            "otp": otp,
            "type": "otp_verification"
        }
        
        # Send to Kafka topic "email-queue"
        future = producer.send(EMAIL_QUEUE_TOPIC, message)
        
        # Wait for send to complete (with timeout)
        future.get(timeout=10)
        
        print(f"Email task queued for {to_email}")
        return True
        
    except KafkaError as e:
        print(f"Failed to send to Kafka: {e}")
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

