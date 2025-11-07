"""
Test script to send a test message to RabbitMQ
"""

import pika
import json
import os


def send_test_message():
    # Get connection parameters from environment variables
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
    queue_name = os.getenv("FILE_PROCESSING_QUEUE", "file_processing_queue")

    # Establish connection to RabbitMQ
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
    )

    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare queue (creates if doesn't exist)
        channel.queue_declare(queue=queue_name, durable=True)

        # Create test message with file path instead of content
        test_message = {
            "file_id": "test-12345",
            "file_name": "test_document.txt",
            "file_path": "../backend/uploads/test_document.txt",
            "file_type": "text/plain",
        }

        # Send message
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(test_message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
        )

        print("Test message sent successfully!")
        print(f"Message: {test_message}")

        # Close connection
        connection.close()

    except Exception as e:
        print(f"Error sending test message: {e}")


if __name__ == "__main__":
    send_test_message()
