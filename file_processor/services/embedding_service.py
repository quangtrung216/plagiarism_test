from sentence_transformers import SentenceTransformer
_model = None

def load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("huyydangg/DEk21_hcmute_embedding")
    return _model

def embed_texts(texts: list) -> list:
    model = load_model()
    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True
    )
    return vectors

def embed_text(text: str) -> list:
    model = load_model()

    vector = model.encode(
        [text],
        normalize_embeddings=True
    )[0]

    return vector.tolist()