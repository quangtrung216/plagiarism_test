import pika
import json
import os
import time
from typing import Dict, Any
from minio import Minio
from minio.error import S3Error

# MinIO configuration from environment variables
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "plagiarism-files")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)


def process_file(file_data: Dict[str, Any]) -> bool:
    """
    Process a file received from RabbitMQ by reading it from MinIO
    This is where the actual file processing logic would be implemented
    """
    try:
        object_name = file_data.get("object_name")
        if not object_name:
            print("Object name not provided in message")
            return False

        print(f"Processing file: {file_data.get('file_name', 'Unknown')}")
        print(f"File ID: {file_data.get('file_id', 'Unknown')}")
        print(f"Object name: {object_name}")
        print(f"File type: {file_data.get('file_type', 'Unknown')}")

        # Retrieve file from MinIO
        try:
            response = minio_client.get_object(MINIO_BUCKET_NAME, object_name)
            content = response.data.decode("utf-8", errors="ignore")
            response.close()
            response.release_conn()
        except S3Error as e:
            print(f"MinIO error retrieving file: {e}")
            return False
        except Exception as e:
            print(f"Error retrieving file from MinIO: {e}")
            return False

        print(f"File size: {len(content)} characters")

        # Simulate file processing
        time.sleep(2)

        # Here you would implement the actual plagiarism detection logic
        # For now, we'll just print a success message
        print(f"File {file_data.get('file_name', 'Unknown')} processed successfully")

        # Optionally, delete the file from MinIO after processing
        # try:
        #     minio_client.remove_object(MINIO_BUCKET_NAME, object_name)
        #     print(f"File {object_name} deleted from MinIO")
        # except S3Error as e:
        #     print(f"MinIO error deleting file: {e}")

        return True
    except Exception as e:
        print(f"Error processing file: {e}")
        return False


def callback(ch, method, properties, body):
    """
    Callback function to handle incoming messages from RabbitMQ
    """
    try:
        # Parse the message
        file_data = json.loads(body.decode("utf-8"))

        # Process the file
        success = process_file(file_data)

        if success:
            print("File processing completed successfully")
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("File processing failed")
            # Reject the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    except json.JSONDecodeError:
        print("Invalid JSON in message")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"Error in callback: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    """
    Start the RabbitMQ consumer
    """
    # Get connection parameters from environment variables
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
    queue_name = os.getenv("FILE_PROCESSING_QUEUE", "file_processing_queue")
    prefetch_count = int(os.getenv("PREFETCH_COUNT", "1"))

    # Establish connection to RabbitMQ
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
    )

    connection = None
    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Declare queue (creates if doesn't exist)
            channel.queue_declare(queue=queue_name, durable=True)

            # Set QoS to limit number of unacknowledged messages
            channel.basic_qos(prefetch_count=prefetch_count)

            # Set up consumer
            channel.basic_consume(queue=queue_name, on_message_callback=callback)

            print(f"Waiting for messages in {queue_name}. To exit press CTRL+C")
            channel.start_consuming()

        except Exception as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            if connection and connection.is_open:
                connection.close()
            time.sleep(5)
        except KeyboardInterrupt:
            print("Interrupted. Closing connection...")
            if connection and connection.is_open:
                connection.close()
            break


if __name__ == "__main__":
    start_consumer()
