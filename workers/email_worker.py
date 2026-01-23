"""
Email Worker (Kafka Consumer)
=============================
This runs as a separate process and listens for email tasks from Kafka.
When a message arrives, it sends the actual email.

Run this with: python workers/email_worker.py
"""
import os
import sys
import json

# Add parent directory to path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from utils.email_sender import send_otp_email


def start_email_worker():
    """
    Start the email worker.
    This will continuously listen for messages and send emails.
    """
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    print(f"Connecting to Kafka at {bootstrap_servers}...")
    
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
            print(f"  To: {data['to']}")
            print(f"  Type: {data.get('type', 'unknown')}")
            
            try:
                # Send the actual email
                send_otp_email(data['to'], data['otp'])
                print(f"  ✓ Email sent successfully!\n")
                
            except Exception as e:
                print(f"  ✗ Failed to send email: {e}\n")
                # In production, you might want to:
                # - Retry the message
                # - Send to a dead-letter queue
                # - Alert someone
                
    except KafkaError as e:
        print(f"Kafka error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down email worker...")
        sys.exit(0)


if __name__ == "__main__":
    start_email_worker()
