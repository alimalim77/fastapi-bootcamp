"""
Email Worker (Kafka Consumer)
=============================
This runs as a separate process and listens for email tasks from Kafka.
When a message arrives, it sends the actual email.

Features:
- Retry with exponential backoff (3 attempts)
- Dead Letter Queue for failed messages

Run this with: python workers/email_worker.py
"""
import os
import sys
import json
import time

# Add parent directory to path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from utils.email_sender import send_otp_email
from utils.kafka_producer import send_to_dlq


# Retry configuration
MAX_RETRIES = 3
BACKOFF_BASE = 1  # Base delay in seconds (1s, 2s, 4s)


def process_email_with_retry(data: dict) -> bool:
    """
    Process email task with retry logic and exponential backoff.
    
    Args:
        data: Message data containing 'to' and 'otp'
    
    Returns:
        True if email sent successfully, False if all retries failed
    """
    to_email = data.get('to')
    otp = data.get('otp')
    last_error = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            send_otp_email(to_email, otp)
            print(f"  ✓ Email sent successfully on attempt {attempt}!\n")
            return True
            
        except Exception as e:
            last_error = e
            print(f"  ✗ Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            
            if attempt < MAX_RETRIES:
                delay = BACKOFF_BASE * (2 ** (attempt - 1))  # 1s, 2s, 4s
                print(f"    Retrying in {delay}s...")
                time.sleep(delay)
    
    # All retries exhausted - send to DLQ
    print(f"  ⚠ All {MAX_RETRIES} attempts failed. Sending to DLQ...")
    send_to_dlq(data, str(last_error), MAX_RETRIES)
    print()
    return False


def start_email_worker():
    """
    Start the email worker.
    This will continuously listen for messages and send emails.
    """
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    print(f"Connecting to Kafka at {bootstrap_servers}...")
    print(f"Retry config: max_retries={MAX_RETRIES}, backoff_base={BACKOFF_BASE}s")
    
    try:
        # Create consumer
        consumer = KafkaConsumer(
            "email-queue",  # Topic to listen to
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id="email-workers",  # Consumer group for load balancing
            auto_offset_reset="earliest"  # Start from beginning if no offset
        )
        
        print("Email worker started! Waiting for messages...")
        print("Press Ctrl+C to stop\n")
        
        # Listen for messages forever
        for message in consumer:
            data = message.value
            
            print(f"Received email task:")
            print(f"  To: {data.get('to', 'unknown')}")
            print(f"  Type: {data.get('type', 'unknown')}")
            
            process_email_with_retry(data)
                
    except KafkaError as e:
        print(f"Kafka error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down email worker...")
        sys.exit(0)


if __name__ == "__main__":
    start_email_worker()

