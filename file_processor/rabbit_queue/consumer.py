import pika
import os
import json
from dotenv import load_dotenv
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from worker.pdf_worker import process_message
load_dotenv()

# Load env
RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBIT_USER = os.getenv("RABBITMQ_USER", "guest")
RABBIT_PASS = os.getenv("RABBITMQ_PASSWORD", "guest")

QUEUE_NAME = os.getenv("FILE_PROCESSING_QUEUE", "file_processing_queue")

RETRY_QUEUE_NAME = os.getenv("FILE_PROCESSING_RETRY_QUEUE", f"{QUEUE_NAME}.retry")
DLQ_NAME = os.getenv("FILE_PROCESSING_DLQ", f"{QUEUE_NAME}.dlq")
RETRY_DELAY_MS = int(os.getenv("FILE_PROCESSING_RETRY_DELAY_MS", "30000"))


def start_consumer():

    print("Starting RabbitMQ consumer...")

    # Login
    credentials = pika.PlainCredentials(
        RABBIT_USER,
        RABBIT_PASS
    )

    params = pika.ConnectionParameters(
        host=RABBIT_HOST,
        port=RABBIT_PORT,
        credentials=credentials
    )

    connection = pika.BlockingConnection(params)

    channel = connection.channel()

    # Declare queue
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True
    )

    channel.queue_declare(
        queue=RETRY_QUEUE_NAME,
        durable=True,
        arguments={
            "x-message-ttl": RETRY_DELAY_MS,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": QUEUE_NAME,
        },
    )

    channel.queue_declare(
        queue=DLQ_NAME,
        durable=True,
    )

    # Only take 1 job at a time
    channel.basic_qos(prefetch_count=1)

    # Register callback
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=process_message
    )

    print(f"Waiting for messages on queue: {QUEUE_NAME}")

    # Start listening
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
