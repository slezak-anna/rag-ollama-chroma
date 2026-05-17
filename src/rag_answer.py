import argparse

from src.ollama_utils import chat
from src.retrieval import advanced_search

def build_context(results: list[dict]) -> str:
    blocks: list[str] = []

    for index, row in enumerate(results, start=1):
        metadata = row["metadata"]

        source = (
            f"[{index}] "
            f"{metadata.get('title')} | "
            f"sekcja: {metadata.get('section')} | "
            f"rok: {metadata.get('year')} | "
            f"plik: {metadata.get('source_file')}"
        )

        blocks.append(
            f"{source}\n{row['text']}"
        )

    return "\n\n".join(blocks)


def answer_question(
    question: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    results = advanced_search(
        question=question,
        history=history or [],
    )

    context = build_context(results)

    prompt = f"""
You are a RAG assistant.
You respond only based on the context provided.

Rules:
1. If the context doesn't provide an answer, write:
"I couldn't find this information in the documents."
2. Don't guess.
3. For facts, provide the source in parentheses, e.g., [1], [2].
4. Answer clearly and concisely.

Context:
{context}

Question:
{question}

Answer:
"""
    return chat(prompt)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--query",
        required=True,
        help="Pytanie do systemu RAG",
    )

    args = parser.parse_args()

    answer = answer_question(args.query)

    print(answer)


if __name__ == "__main__":
    main()