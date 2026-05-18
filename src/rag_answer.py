import argparse

from src.ollama_utils import chat
from src.retrieval import advanced_search, filter_answerable_results

def build_context(results: list[dict]) -> str:
    blocks: list[str] = []

    for index, row in enumerate(results, start=1):
        metadata = row["metadata"]

        source_header = (
            f"[{index}] "
            f"title={metadata.get('title')} | "
            f"section={metadata.get('section')} | "
            f"system={metadata.get('system')} | "
            f"doc_type={metadata.get('doc_type')} | "
            f"status={metadata.get('status')} | "
            f"year={metadata.get('year')} | "
            f"version={metadata.get('version')} | "
            f"file={metadata.get('source_file')}"
        )

        blocks.append(
            f"{source_header}\n"
            f"{row['text']}"
        )

    return "\n\n".join(blocks)


def build_sources(results: list[dict]) -> str:
    lines: list[str] = []

    for index, row in enumerate(results, start=1):
        metadata = row["metadata"]

        lines.append(
            f"[{index}] {metadata.get('title')} — "
            f"section: {metadata.get('section')}, "
            f"system: {metadata.get('system')}, "
            f"status: {metadata.get('status')}, "
            f"year: {metadata.get('year')}, "
            f"version: {metadata.get('version')}, "
            f"file: {metadata.get('source_file')}"
        )

    return "\n".join(lines)


def answer_question(
    question: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    raw_results = advanced_search(
        question=question,
        history=history or [],
    )

    results = filter_answerable_results(raw_results)

    if not results:
        return (
            "I could not find reliable information in the available documents.\n\n"
            "Sources checked: no retrieved chunk passed the minimum relevance threshold."
        )

    context = build_context(results)
    sources = build_sources(results)

    prompt = f"""
You are a careful RAG assistant.

Answer the user's question using ONLY the context below.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain the answer, say:
   "I could not find this information in the available documents."
3. Cite sources using [1], [2], [3] after factual claims.
4. Prefer active documents over archived documents.
5. If a document is archived, explicitly mention that it is archived.
6. Keep the answer clear and structured.

Context:
{context}

Question:
{question}

Answer:
"""

    answer = chat(prompt)

    return (
        f"{answer.strip()}\n\n"
        f"Sources used:\n{sources}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--query",
        required=True,
        help="Question to ask the RAG system",
    )

    args = parser.parse_args()

    print(answer_question(args.query))


if __name__ == "__main__":
    main()