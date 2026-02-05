import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()


def publish_task(data):

    host = os.getenv("RABBITMQ_HOST")
    port = int(os.getenv("RABBITMQ_PORT"))
    user = os.getenv("RABBITMQ_USER")
    password = os.getenv("RABBITMQ_PASSWORD")
    queue = os.getenv("FILE_PROCESSING_QUEUE")

    credentials = pika.PlainCredentials(user, password)

    params = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials
    )

    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    ch.queue_declare(queue=queue, durable=True)

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
