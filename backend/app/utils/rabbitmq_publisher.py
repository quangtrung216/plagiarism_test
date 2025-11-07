"""
Example of how to integrate RabbitMQ publishing in the main backend application
This would be added to a service or utility module in the backend application
"""

import pika
import json
from typing import Dict, Any
from app.core.config import settings


def send_file_for_processing(file_data: Dict[str, Any]) -> bool:
    """
    Send a file processing request to RabbitMQ
    This function would be called when a file is uploaded through the API

    Args:
        file_data: Dictionary containing file information
            {
                "file_id": "unique_identifier",
                "file_name": "document.txt",
                "object_name": "uuid4_extension",
                "file_type": "text/plain"
            }

    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        # Get connection parameters from settings
        rabbitmq_host = settings.RABBITMQ_HOST
        rabbitmq_port = settings.RABBITMQ_PORT
        rabbitmq_user = settings.RABBITMQ_USER
        rabbitmq_password = settings.RABBITMQ_PASSWORD
        queue_name = settings.FILE_PROCESSING_QUEUE

        # Establish connection to RabbitMQ
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare queue (creates if doesn't exist)
        channel.queue_declare(queue=queue_name, durable=True)

        # Send message
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(file_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
        )

        # Close connection
        connection.close()

        return True

    except Exception as e:
        print(f"Error sending file for processing: {e}")
        return False


# Example usage:
# file_info = {
#     "file_id": "12345",
#     "file_name": "document.txt",
#     "object_name": "uuid4_extension",
#     "file_type": "text/plain"
# }
# success = send_file_for_processing(file_info)
# if success:
#     print("File sent for processing")
# else:
#     print("Failed to send file for processing")
