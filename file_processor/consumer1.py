# consumer.py
import pika
import json
import numpy as np
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize

# Khởi tạo mô hình (chỉ load 1 lần)
print("Loading embedding model...")
model = SentenceTransformer('dangvantuan/vietnamese-embedding')
print("Model loaded.")

# MinIO client
minio_client = Minio(
    "localhost:9000",  # hoặc "plagiarism_minio:9000" nếu trong Docker
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

BUCKET_NAME = "embedding"

# Tạo bucket nếu chưa có
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)
    print(f"Bucket {BUCKET_NAME} created.")

def process_message(ch, method, properties, body):
    try:
        data = json.loads(body)
        file_id = data["file_id"]
        text = data["text"]

        print(f"Processing file_id: {file_id}")

        # Tokenize (nếu cần – mô hình này đã được fine-tune trên tiếng Việt, có thể không cần)
        # Nhưng bạn đã dùng tokenize ở ví dụ → giữ để nhất quán
        tokenized = tokenize(text)
        embedding = model.encode([tokenized])[0]  # shape: (768,)

        # Chuyển embedding thành bytes (.npy)
        buffer = BytesIO()
        np.save(buffer, embedding)
        buffer.seek(0)

        # Upload lên MinIO
        minio_client.put_object(
            BUCKET_NAME,
            f"{file_id}.npy",
            buffer,
            length=buffer.getbuffer().nbytes,
            content_type="application/octet-stream"
        )

        print(f"Embedding for {file_id} saved to MinIO.")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delelivery_tag=method.delivery_tag, requeue=False)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="embedding_queue", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="embedding_queue", on_message_callback=process_message)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    main()