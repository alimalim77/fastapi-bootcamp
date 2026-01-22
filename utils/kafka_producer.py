"""
Kafka Producer for Email Queue
==============================
Sends email tasks to Kafka for async processing.
The email worker (consumer) will pick up these messages and send the actual emails.
"""
import os
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError


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
        future = producer.send("email-queue", message)
        
        # Wait for send to complete (with timeout)
        future.get(timeout=10)
        
        print(f"Email task queued for {to_email}")
        return True
        
    except KafkaError as e:
        print(f"Failed to send to Kafka: {e}")
        return False
    
    finally:
        producer.close()
