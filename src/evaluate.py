import json

import pandas as pd

from src.config import settings
from src.retrieval import hybrid_search, self_query, vector_search


def load_eval_questions() -> list[dict]:
    path = settings.EVAL_DIR / "questions.jsonl"

    rows: list[dict] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))

    return rows


def is_relevant(
    result: dict,
    expected_doc_id: str,
    expected_section_contains: str,
) -> bool:
    metadata = result["metadata"]

    same_document = metadata.get("doc_id") == expected_doc_id

    section_matches = expected_section_contains.lower() in str(
        metadata.get("section", "")
    ).lower()

    return same_document and section_matches


def calculate_metrics(
    results: list[dict],
    expected_doc_id: str,
    expected_section_contains: str,
    k: int,
) -> tuple[float, float, float]:
    top_k = results[:k]

    relevance = [
        is_relevant(
            result=row,
            expected_doc_id=expected_doc_id,
            expected_section_contains=expected_section_contains,
        )
        for row in top_k
    ]

    recall_at_k = 1.0 if any(relevance) else 0.0
    precision_at_k = sum(relevance) / k

    reciprocal_rank = 0.0

    for index, is_good in enumerate(relevance, start=1):
        if is_good:
            reciprocal_rank = 1.0 / index
            break

    return recall_at_k, precision_at_k, reciprocal_rank


def evaluate_mode(mode: str, k: int = 5) -> tuple[list[dict], list[dict]]:
    questions = load_eval_questions()

    metric_rows: list[dict] = []
    failures: list[dict] = []

    for item in questions:
        question = item["question"]
        expected_doc_id = item["expected_doc_id"]
        expected_section_contains = item["expected_section_contains"]

        if mode == "vector":
            results = vector_search(
                query=question,
                top_k=k,
            )

        elif mode == "hybrid":
            parsed = self_query(question)

            results = hybrid_search(
                query=parsed["query"],
                top_k=k,
                filters=parsed["filters"],
            )

        else:
            raise ValueError("mode must be either: vector or hybrid")

        recall, precision, reciprocal_rank = calculate_metrics(
            results=results,
            expected_doc_id=expected_doc_id,
            expected_section_contains=expected_section_contains,
            k=k,
        )

        metric_rows.append(
            {
                "mode": mode,
                "question": question,
                f"recall@{k}": recall,
                f"precision@{k}": precision,
                "rr": reciprocal_rank,
            }
        )

        if recall == 0.0:
            failures.append(
                {
                    "mode": mode,
                    "question": question,
                    "expected_doc_id": expected_doc_id,
                    "expected_section_contains": expected_section_contains,
                    "returned": [
                        {
                            "id": row["id"],
                            "doc_id": row["metadata"].get("doc_id"),
                            "section": row["metadata"].get("section"),
                            "score": row.get("score"),
                            "text_start": row["text"][:300],
                        }
                        for row in results
                    ],
                }
            )

    return metric_rows, failures


def main() -> None:
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    all_failures: list[dict] = []

    for mode in ["vector", "hybrid"]:
        rows, failures = evaluate_mode(
            mode=mode,
            k=5,
        )

        all_rows.extend(rows)
        all_failures.extend(failures)

    df = pd.DataFrame(all_rows)

    print()
    print("Detailed results:")
    print(df.to_string(index=False))

    print()
    print("Summary:")
    print(
        df.groupby("mode").mean(numeric_only=True).to_string()
    )

    failure_path = settings.REPORTS_DIR / "failures.json"

    failure_path.write_text(
        json.dumps(
            all_failures,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Failure cases saved to: {failure_path}")


if __name__ == "__main__":
    main()