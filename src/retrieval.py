import math
import re
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi

from src.chroma_store import get_all_records, get_collection
from src.config import settings
from src.ollama_utils import chat, embed_text, extract_json_object

def tokenize(text: str) -> list[str]:

    return re.findall(
        r"[\w\-]+",
        text.lower(),
    )

def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}

    values = list(scores.values())
    min_value = min(values)
    max_value = max(values)

    if math.isclose(min_value, max_value):
        return {key: 1.0 for key in scores}

    return {
        key: (value - min_value) / (max_value - min_value)
        for key, value in scores.items()
    }

def build_where_filter(filters: dict[str, Any] | None) -> dict | None:
    if not filters: 
        return None
    
    clean_filters = {
        key: value for key, value in filters.items()
        if value is not None
    }

    if not clean_filters:
        return None
    
    if len(clean_filters) == 1:
        key, value = next(iter(clean_filters.items()))
        return {key: value}
    
    return {
        "$and": [
            {key, value}
            for key, value in clean_filters.items()
        ]
    }

def vector_search(
        query: str,
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
) -> list[dict]:
    
    if top_k is None:
        top_k = settings.VECTOR_TOP_K
        
    collection = get_collection()
    query_embedding = embed_text(query)
    where_filter = build_where_filter(filters)

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    rows: list[dict] = []

    ids = result["ids"][0]
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        distance = float(distance)

        vector_score = 1.0 / (1.0 + distance)

        rows.append(
            {
                "id": chunk_id,
                "text": document,
                "metadata": metadata,
                "distance": distance,
                "vector_score": vector_score,
                "score": vector_score,               
            }
        )

    return rows

def bm25_search(
        query:str, 
        top_k: int | None = None,
        filters: dict[str, Any] | None = None,
) -> list[dict]:
    
    top_k = top_k or settings.HYBRID_CANDIDATES

    records = get_all_records()

    items: list[dict] = []

    for chunk_id, document, metadata in zip(
        records["ids"],
        records["documents"],
        records["metadatas"],
    ):
        if filters:
            should_skip = False

            for key, value in filters.items():
                if value is not None and metadata.get(key) != value:
                    should_skip = True
                    break

            if should_skip:
                continue

        items.append(
            {
                "id": chunk_id,
                "text": document,
                "metadata": metadata,
            }
        )

    if not items:
        return []

    tokenized_corpus = [
        tokenize(item["text"])
        for item in items
    ]

    tokenized_query = tokenize(query)

    if not tokenized_query:
        return []

    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)

    ranked_indexes = np.argsort(scores)[::-1][:top_k]

    rows: list[dict] = []

    for index in ranked_indexes:
        index = int(index)
        score = float(scores[index])

        if score <= 0:
            continue

        rows.append(
            {
                **items[index],
                "bm25_score": score,
                "score": score,
            }
        )

    return rows

def hybrid_search(
    query: str,
    top_k: int | None = None,
    candidates: int | None = None,
    filters: dict[str, Any] | None = None,
) -> list[dict]:
    
    top_k = top_k or settings.FINAL_TOP_K
    candidates = candidates or settings.HYBRID_CANDIDATES

    vector_results = vector_search(
        query=query,
        top_k=candidates,
        filters=filters,
    )

    bm25_results = bm25_search(
        query=query,
        top_k=candidates,
        filters=filters,
    )

    vector_scores = {
        row["id"]: row.get("vector_score", 0.0)
        for row in vector_results
    }

    bm25_scores = {
        row["id"]: row.get("bm25_score", 0.0)
        for row in bm25_results
    }

    vector_scores = normalize_scores(vector_scores)
    bm25_scores = normalize_scores(bm25_scores)
    by_id: dict[str, dict] = {}

    for row in vector_results + bm25_results:
        chunk_id = row["id"]

        if chunk_id not in by_id:
            by_id[chunk_id] = {
                "id": chunk_id,
                "text": row["text"],
                "metadata": row["metadata"],
                "vector_score": 0.0,
                "bm25_score": 0.0,
                "score": 0.0,
            }

    for chunk_id, row in by_id.items():
        row["vector_score"] = vector_scores.get(chunk_id, 0.0)
        row["bm25_score"] = bm25_scores.get(chunk_id, 0.0)

        row["score"] = (
            settings.VECTOR_WEIGHT * row["vector_score"]
            + settings.BM25_WEIGHT * row["bm25_score"]
        )

    ranked = sorted(
        by_id.values(),
        key=lambda row: row["score"],
        reverse=True,
    )

    return ranked[:top_k]

def contextualize_query(
    history: list[dict[str, str]],
    question: str,
) -> str:
    
    if not history:
        return question

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history[-6:]
    )

    prompt = f"""
    Rewrite the user's question so that it is self-contained and unambiguous.
    Do not answer the question.
    Return only the rewritten question.

    Conversation history:
    {history_text}

    New question:
    {question}
    """

    rewritten = chat(prompt).strip()

    return rewritten or question

def expand_query(question: str) -> list[str]:
    prompt = f"""
    Generate 3 short variants of a query for the RAG search engine.
    Include synonyms and technical terms.
    Return only JSON in the following format:
    {{"queries": ["...", "...", "..."]}}

    Question:
    {question}
    """

    data = extract_json_object(chat(prompt))
    queries = data.get("queries", [])

    cleaned_queries = []

    for query in queries:
        if isinstance(query, str) and query.strip():
            cleaned_queries.append(query.strip())

    return [question] + cleaned_queries[:3]

def self_query(question: str) -> dict:

    filters: dict[str, Any] = {}
    lowered = question.lower()

    year_match = re.search(r"\b(2024|2025|2026|2027)\b", question)

    if year_match:
        filters["year"] = int(year_match.group(1))

    if "politician" in lowered:
        filters["doc_type"] = "policy"
    elif "procedures" in lowered:
        filters["doc_type"] = "procedure"
    elif "err_" in lowered or "error" in lowered or "error" in lowered:
        filters["doc_type"] = "technical"

    cleaned_query = re.sub(
        r"\b(2024|2025|2026|2027)\b",
        "",
        question,
    ).strip()

    return {
        "query": cleaned_query,
        "filters": filters,
    }

def rerank_with_ollama(
    question: str,
    candidates: list[dict],
    top_k: int | None = None,
) -> list[dict]:

    top_k = top_k or settings.FINAL_TOP_K

    reranked: list[dict] = []

    for row in candidates[:settings.RERANK_TOP_N]:
        prompt = f"""
Rate the relevance of the fragment to the question.
Return only one number:
0 - not relevant
1 - not very helpful
2 - partially relevant
3 - very relevant

Question:
{question}

Fragment:
{row["text"]}
"""
        answer = chat(prompt).strip()
        match = re.search(r"[0-3]", answer)

        relevance = int(match.group(0)) if match else 0

        new_row = dict(row)
        new_row["rerank_score"] = relevance

        new_row["score"] = relevance + 0.01 * float(row.get("score", 0.0))

        reranked.append(new_row)

    ranked = sorted(
        reranked,
        key=lambda row: row["score"],
        reverse=True,
    )

    return ranked[:top_k]

def advanced_search(
    question: str,
    history: list[dict[str, str]] | None = None,
) -> list[dict]:
    """
    Full retrieval:
    1. contextual search,
    2. self-query,
    3. query expansion,
    4. hybrid search,
    5. reranking.
    """
    history = history or []

    contextual_question = contextualize_query(
        history=history,
        question=question,
    )

    parsed = self_query(contextual_question)

    base_query = parsed["query"]
    filters = parsed["filters"]

    expanded_queries = expand_query(base_query)

    candidates_by_id: dict[str, dict] = {}

    for query_variant in expanded_queries:
        results = hybrid_search(
            query=query_variant,
            top_k=settings.HYBRID_CANDIDATES,
            filters=filters,
        )

        for row in results:
            chunk_id = row["id"]

            if (
                chunk_id not in candidates_by_id
                or row["score"] > candidates_by_id[chunk_id]["score"]
            ):
                candidates_by_id[chunk_id] = row

    candidates = sorted(
        candidates_by_id.values(),
        key=lambda row: row["score"],
        reverse=True,
    )

    return rerank_with_ollama(
        question=contextual_question,
        candidates=candidates,
        top_k=settings.FINAL_TOP_K,
    )