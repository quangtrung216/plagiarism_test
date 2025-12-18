# main.py
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from typing import List
import pika
import json
import uuid

app = FastAPI(title="Text Embedding Ingestion API")

RABBITMQ_HOST = "localhost"  # hoặc "plagiarism_rabbitmq" nếu chạy trong Docker cùng network
QUEUE_NAME = "embedding_queue"

def send_to_rabbitmq(file_id: str, text: str):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        message = json.dumps({"file_id": file_id, "text": text})
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # persistent
        )
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RabbitMQ error: {str(e)}")

@app.post("/upload-texts/")
async def upload_texts(
    file_ids: List[str] = Form(...),
    files: List[UploadFile] = File(...)
):
    if len(file_ids) != len(files):
        raise HTTPException(status_code=400, detail="Number of file_ids must match number of files")

    results = []
    for file_id, file in zip(file_ids, files):
        content = (await file.read()).decode("utf-8")
        send_to_rabbitmq(file_id, content)
        results.append({"file_id": file_id, "status": "queued"})

    return {"message": "Files queued for embedding processing", "details": results}