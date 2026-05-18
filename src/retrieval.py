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


def reciprocal_rank(rank: int, k: int | None = None) -> float:
    k = k or settings.RRF_K
    return 1.0 / (k + rank)

def rrf_fusion(
    ranked_lists: list[list[dict]],
    top_k: int,
) -> list[dict]:
    fused: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, row in enumerate(ranked_list, start=1):
            chunk_id = row["id"]

            if chunk_id not in fused:
                fused[chunk_id] = {
                    "id": chunk_id,
                    "text": row["text"],
                    "metadata": row["metadata"],
                    "vector_score": None,
                    "bm25_score": None,
                    "vector_rank": None,
                    "bm25_rank": None,
                    "rrf_score": 0.0,
                    "retrieval_sources": [],
                }

            fused[chunk_id]["rrf_score"] += reciprocal_rank(rank)

            if row.get("retrieval_method") == "vector":
                fused[chunk_id]["vector_score"] = row.get("vector_score")
                fused[chunk_id]["vector_rank"] = rank
                fused[chunk_id]["retrieval_sources"].append("vector")

            if row.get("retrieval_method") == "bm25":
                fused[chunk_id]["bm25_score"] = row.get("bm25_score")
                fused[chunk_id]["bm25_rank"] = rank
                fused[chunk_id]["retrieval_sources"].append("bm25")

    ranked = sorted(
        fused.values(),
        key=lambda row: row["rrf_score"],
        reverse=True,
    )

    for row in ranked:
        row["score"] = row["rrf_score"]
        row["retrieval_method"] = "rrf_hybrid"

    return ranked[:top_k]


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

    return rrf_fusion(
        ranked_lists=[
            vector_results,
            bm25_results,
        ],
        top_k=top_k,
    )


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
    elif "err_" in lowered or "error" in lowered:
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


def safe_json_from_llm(prompt: str) -> dict:
    raw = chat(prompt).strip()
    data = extract_json_object(raw)

    if not isinstance(data, dict):
        return {}

    return data


def rerank_with_ollama(
    question: str,
    candidates: list[dict],
    top_k: int | None = None,
) -> list[dict]:
    """
    Reranking z uzasadnieniem.

    Model zwraca:
    {
      "score": 0-3,
      "reason": "..."
    }
    """
    top_k = top_k or settings.FINAL_TOP_K

    reranked: list[dict] = []

    for row in candidates[: settings.RERANK_TOP_N]:
        metadata = row["metadata"]

        prompt = f"""
You are a strict RAG reranker.

Evaluate how relevant the chunk is for the user's question.

Score:
0 = irrelevant
1 = weakly related
2 = useful but incomplete
3 = directly answers the question

Return only valid JSON:
{{"score": 0, "reason": "short reason"}}

Question:
{question}

Chunk metadata:
title: {metadata.get("title")}
section: {metadata.get("section")}
system: {metadata.get("system")}
doc_type: {metadata.get("doc_type")}
status: {metadata.get("status")}
year: {metadata.get("year")}

Chunk:
{row["text"]}
"""

        data = safe_json_from_llm(prompt)

        try:
            rerank_score = int(data.get("score", 0))
        except (TypeError, ValueError):
            rerank_score = 0

        rerank_score = max(0, min(3, rerank_score))

        reason = str(data.get("reason", "")).strip()

        new_row = dict(row)
        new_row["rerank_score"] = rerank_score
        new_row["rerank_reason"] = reason

        new_row["score"] = rerank_score + 0.01 * float(row.get("rrf_score", 0.0))

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

def filter_answerable_results(results: list[dict]) -> list[dict]:

    filtered = []

    for row in results:
        rerank_score = row.get("rerank_score")

        if rerank_score is None:
            filtered.append(row)
            continue

        if rerank_score >= settings.MIN_RERANK_SCORE:
            filtered.append(row)

    return filtered