import argparse

from src.retrieval import advanced_search, hybrid_search, self_query, vector_search


def print_results(results: list[dict]) -> None:

    print(f"Number of results: {len(results)}")

    if not results:
        print("No results found.")
        return

    for index, row in enumerate(results, start=1):
        metadata = row["metadata"]

        print("=" * 80)
        print(f"RESULT {index}")
        print(f"ID: {row['id']}")
        print(f"Final score: {row.get('score')}")
        print(f"RRF score: {row.get('rrf_score')}")
        print(f"Vector score: {row.get('vector_score')}")
        print(f"Vector rank: {row.get('vector_rank')}")
        print(f"BM25 score: {row.get('bm25_score')}")
        print(f"BM25 rank: {row.get('bm25_rank')}")
        print(f"Rerank score: {row.get('rerank_score')}")
        print(f"Rerank reason: {row.get('rerank_reason')}")
        print(
            "Source:",
            metadata.get("title"),
            "| section:",
            metadata.get("section"),
            "| system:",
            metadata.get("system"),
            "| status:",
            metadata.get("status"),
            "| year:",
            metadata.get("year"),
            "| type:",
            metadata.get("doc_type"),
        )
        print("-" * 80)
        print(row["text"][:1200])
        print()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--query",
        required=True,
        help="User question",
    )

    parser.add_argument(
        "--mode",
        choices=["vector", "hybrid", "advanced"],
        default="vector",
    )

    args = parser.parse_args()

    if args.mode == "vector":
        results = vector_search(args.query)

    elif args.mode == "hybrid":
        parsed = self_query(args.query)

        print("Self-query result:")
        print(parsed)

        results = hybrid_search(
            query=parsed["query"],
            filters=parsed["filters"],
        )

    else:
        results = advanced_search(args.query)

    print_results(results)


if __name__ == "__main__":
    main()