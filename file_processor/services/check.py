from model.check import MatchedSementicUnit, ReferenceMatch, Response, SentenceRecord
from db.milvus import connect  
from nlp import text_preprocess
from pymilvus import Collection
from sklearn.metrics.pairwise import cosine_similarity

s_threshold = 0.8
doc_threshold = 0.8

def check(
    query_sentences: list[SentenceRecord],
    query_embeddings: list[list[float]],
    candidates: list[dict],                    # {document_id, file_name, subject_id, jaccard_similarity}
    sentence_labels: list[int],         # mảng nhãn 0/1, được cập nhật in-place
) -> list[ReferenceMatch]:
    plagiarized_count = 0

    connect()
    collection = Collection("plagiarism_sentences")
    collection.load()
    # # Query Milvus: với mỗi câu của d, tìm câu giống nhất trong d1
    # match_results = milvus_repo.search_similar_sentences(
    #     query_embeddings=query_embeddings,
    #     document_ids=document_ids,
    #     top_k=1,
    #     similarity_threshold=SENTENCE_SIMILARITY_THRESHOLD,
    # )
    reference_matches: list[ReferenceMatch] = []
    for candidate in candidates:
        reference_matches.append(ReferenceMatch(
            document_id=candidate["document_id"],
            file_name=candidate["file_name"],
            subject_id=candidate["subject_id"],
            jaccard_similarity=candidate["jaccard_similarity"],
            plagiarism_ratio=0.0,
            plagiarized_count=0,
            matched_sentences=[],
        ))
    reference_map = {m.document_id: m for m in reference_matches}
    c = 0
    for s in query_embeddings:
        for candidate in candidates:
            d = candidate["document_id"]
            results = collection.query(
                output_fields=["embedding", "text"],
                expr=f"document_id == '{d}'",
            )
            d_embeddings = [item["embedding"] for item in results]
            d_sentence_texts = [item["text"] for item in results]
            i = 0
            for s2 in d_embeddings:
                # Tính cosine similarity giữa s và s2
                sim = cosine_similarity([s], [s2])[0][0]
                if sim >= s_threshold:
                    # Câu này bị đạo văn từ tài liệu tham chiếu
                    if sentence_labels[c] == 1:
                        break  # chỉ gán nhãn đạo văn 1 lần cho mỗi câu
                    sentence_labels[c] = 1
                    plagiarized_count += 1
                    if d in reference_map:
                        reference_map[d].plagiarized_count += 1
                        reference_map[d].plagiarism_ratio = round(reference_map[d].plagiarized_count / len(query_sentences), 4) if len(query_sentences) > 0 else 0.0
                        reference_map[d].matched_sentences.append(MatchedSementicUnit(
                            query_sentence_index=c,
                            query_sentence_text=query_sentences[c].text,
                            query_page=1,
                            ref_sentence_text=d_sentence_texts[i],
                            ref_page=1,
                            similarity=sim,
                        ))
                i += 1
        c += 1
    reference_matches = [m for m in reference_matches if m.plagiarized_count > 0]  # chỉ giữ tài liệu tham chiếu có đạo văn
    return reference_matches

def run_plagiarism_check(
    query_sentences: list[SentenceRecord],
    query_embeddings: list[list[float]],
    candidates: list[dict],
) -> Response:
    """
    Chạy toàn bộ luồng so khớp chi tiết.
    candidates: danh sách tài liệu tham chiếu đã qua lọc thô MinHash.
    """
    total_sentences = len(query_sentences)
    sentence_labels = [0] * total_sentences   # 0 = chưa đạo văn, 1 = đạo văn
    references: list[ReferenceMatch] = []

    ref_match = check(
            query_sentences=query_sentences,
            query_embeddings=query_embeddings,
            candidates=candidates,
            sentence_labels=sentence_labels,
        )

    return Response(
        total_sentences=total_sentences,
        plagiarized_sentences=sum(m.plagiarized_count for m in ref_match),
        plagiarism_ratio=round(sum(m.plagiarized_count for m in ref_match) / total_sentences, 4) if total_sentences > 0 else 0.0,
        is_plagiarized=round(sum(m.plagiarized_count for m in ref_match) / total_sentences, 4) > doc_threshold if total_sentences > 0 else False,
        sentence_labels=sentence_labels,
        references=ref_match,
    )