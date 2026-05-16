import argparse

from src.retrieval import advanced_search, hybrid_search, self_query, vector_search
def print_results(results: list[dict]) -> None:
    for index, row in enumerate(results, start=1):
        metadata = row["metadata"]

        print("=" * 80)
        print(f"RESULT {index}")
        print(f"ID: {row['id']}")
        print(f"Score: {row.get('score')}")
        print(f"Vector score: {row.get('vector_score')}")
        print(f"BM25 score: {row.get('bm25_score')}")
        print(f"Rerank score: {row.get('rerank_score')}")
        print(
            "Source:",
            metadata.get("title"),
            "| section:",
            metadata.get("section"),
            "| year:",
            metadata.get("year"),
            "| type:",
            metadata.get("doc_type"),
        )
        print("-" * 80)
        print(row["text"][:1000])
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

        results = hybrid_search(
            query=parsed["query"],
            filters=parsed["filters"],
        )

    else:
        results = advanced_search(args.query)

    print_results(results)


if __name__ == "__main__":
    main()