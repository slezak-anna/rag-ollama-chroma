import chromadb

from src.chunking import Chunk
from src.config import settings

def get_client():
    settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(settings.CHROMA_DIR)
    )

def get_collection():
    client = get_client()

    return client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )

def reset_collection():
    client = get_client()

    try:
        client.delete_collection(settings.COLLECTION_NAME)
    except Exception:
        pass

    return client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )

def add_chunks_to_chroma(
    chunks: list[Chunk],
    embeddings: list[list[float]],
    reset: bool = False,
) -> None:
    if reset:
        collection = reset_collection()
    else:
        collection = get_collection()

    collection.add(
        ids=[chunk.id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
        embeddings=embeddings,
    )

    print(f"Saved {len(chunks)} chunks to Chroma.")

def get_all_records() -> dict:
    collection = get_collection()

    return collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )
