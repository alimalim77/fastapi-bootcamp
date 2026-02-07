"""
Email Worker (Kafka Consumer)
=============================
This runs as a separate process and listens for email tasks from Kafka.
When a message arrives, it sends the actual email.

Features:
- Retry with exponential backoff (3 attempts)
- Dead Letter Queue for failed messages
- Prometheus metrics for monitoring

Run this with: python workers/email_worker.py
"""
import os
import sys
import json
import time
import threading

# Add parent directory to path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from prometheus_client import start_http_server, Counter
from utils.email_sender import send_otp_email
from utils.kafka_producer import send_to_dlq
from utils.metrics import increment_email_attempt, observe_email_processing_time


# Retry configuration
MAX_RETRIES = 3
BACKOFF_BASE = 1  # Base delay in seconds (1s, 2s, 4s)
METRICS_PORT = 8001


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
    start_time = time.time()
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            send_otp_email(to_email, otp)
            print(f"  ✓ Email sent successfully on attempt {attempt}!\n")
            
            # Record success metrics
            duration = time.time() - start_time
            increment_email_attempt(success=True)
            observe_email_processing_time(duration)
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
    
    # Record failure metrics
    duration = time.time() - start_time
    increment_email_attempt(success=False)
    observe_email_processing_time(duration)
    
    print()
    return False


def start_metrics_server():
    """Start Prometheus metrics HTTP server in background thread."""
    print(f"Starting Prometheus metrics server on port {METRICS_PORT}...")
    start_http_server(METRICS_PORT)
    print(f"Metrics available at http://localhost:{METRICS_PORT}/metrics")

# Prometheus Metrics
EMAIL_TASKS_PROCESSED_TOTAL = Counter(
    'email_tasks_processed_total',
    'Total number of email tasks processed',
    ['status']
)


MAX_RETRIES = 3

def start_email_worker():
    """
    Start the email worker.
    """
    # Start metrics server in background
    metrics_thread = threading.Thread(target=start_metrics_server, daemon=True)
    metrics_thread.start()
    
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    # Start Prometheus metrics server
    start_http_server(8001)
    print("Metrics server started on port 8001")
    
    print(f"Connecting to Kafka at {bootstrap_servers}...")
    print(f"Retry config: max_retries={MAX_RETRIES}, backoff_base={BACKOFF_BASE}s")
    
    try:
        consumer = KafkaConsumer(
            "email-queue",
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id="email-workers",
            auto_offset_reset="earliest"
        )
        
        print("Email worker started! Waiting for messages...")
        print("Press Ctrl+C to stop\n")
        
        for message in consumer:
            data = message.value
            retry_count = data.get('retry_count', 0)
            
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

