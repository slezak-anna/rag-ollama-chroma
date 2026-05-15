import chroma_db

from src.chunking import Chunk
from config import settings



def get_client():
    settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    return chroma_db.PersistentClient(
        path=str(settings.CHROMA_DIR)
    )

def get_collection():
    client = get_client()

    return client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )

def reset_collaction():
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
) -> None:
    collection = reset_collaction()

    collection.add(
        ids=[chunk.id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadata=[chunk.metadata for chunk in chunks],
        embeddings=embeddings
    )

    print(f"Saved {len(chunks)} chunks to ChromaDB")

def get_all_records() -> dict:
    collection = get_collection()

    return collection.get(
        include=[
            "documents",
            "metadata",
        ]
    )
