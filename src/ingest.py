from src.chroma_store import add_chunks_to_chroma
from src.chunking import load_and_chunk_markdown_files
from src.config import settings
from src.ollama_utils import embed_texts

def main() -> None:
    chunks = load_and_chunk_markdown_files(raw_dir=settings.DATA_RAW_DIR, 
                                           chunk_size=settings.CHUNK_SIZE_WORDS, 
                                           overlap=settings.CHUNK_OVERLAP_WORDS)
    
    if not chunks:
        raise RuntimeError(
            "Lack of chunks. First run python -m src.generate_data"
        )
    
    embeddings = embed_texts(chunk.text for chunk in chunks)

    add_chunks_to_chroma(chunks=chunks, embeddings=embeddings)

    print("Ingestion is done.")

if __name__ == "__main__":
    main()