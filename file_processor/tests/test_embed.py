from services.embedding_service import embed_texts

texts = [
    "học máy là lĩnh vực quan trọng",
    "machine learning rất phổ biến"
]

vecs = embed_texts(texts)

print(len(vecs))
print(len(vecs[0]))

for i, v in enumerate(vecs[0]):
        print(f"{i}: {v}")

print("\n------------------\n")

print("Vector dạng list:")
print(vecs[0])