from src.chroma_store import add_chunks_to_chroma
from src.chunking import load_and_chunk_markdown_files
from src.config import settings
from src.ollama_utils import embed_text


def main() -> None:
    chunks = load_and_chunk_markdown_files(
        settings.DATA_RAW_DIR,
        settings.CHUNK_SIZE_WORDS,
        settings.CHUNK_OVERLAP_WORDS,
    )

    print(f"Loaded {len(chunks)} chunks from {settings.DATA_RAW_DIR}")

    embeddings = [
        embed_text(chunk.text)
        for chunk in chunks
    ]

    add_chunks_to_chroma(
        chunks=chunks,
        embeddings=embeddings,
        reset=True,
    )


if __name__ == "__main__":
    main()