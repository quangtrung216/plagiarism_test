# test_search.py

from db.milvus import connect, search_vectors
from services.embedding_service import embed_texts

connect()

text = "Giới thiệu về hệ thống phát hiện đạo văn"

vec = embed_texts([text])[0]

results = search_vectors(vec, limit=5)

for r in results:
    print(r)
