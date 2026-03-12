import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()


def publish_task(data):

    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", 5672))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    queue = os.getenv("FILE_PROCESSING_QUEUE", "file_processing_queue")

    retry_queue = os.getenv("FILE_PROCESSING_RETRY_QUEUE", f"{queue}.retry")
    dlq_queue = os.getenv("FILE_PROCESSING_DLQ", f"{queue}.dlq")
    retry_delay_ms = int(os.getenv("FILE_PROCESSING_RETRY_DELAY_MS", "30000"))

    credentials = pika.PlainCredentials(user, password)

    params = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials
    )

    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.queue_declare(queue=queue, durable=True)
    ch.queue_declare(
        queue=retry_queue,
        durable=True,
        arguments={
            "x-message-ttl": retry_delay_ms,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": queue,
        },
    )
    ch.queue_declare(queue=dlq_queue, durable=True)

    ch.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    conn.close()

    print("Published:", data)
