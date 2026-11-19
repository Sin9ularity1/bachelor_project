
from pathlib import Path

import chromadb
import ollama

# Project paths
ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = ROOT / "documents" / "clean"
DATABASE_DIR = ROOT / "data" / "chroma"

# Configuration
EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "rag_documents"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text):
    """Split documents into overlapping chunks."""

    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP

    for start in range(0, len(text), step):
        chunk = text[start:start + CHUNK_SIZE].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def main():
    # Connect to the persistent vector database
    client = chromadb.PersistentClient(
        path=str(DATABASE_DIR)
    )

    # Rebuild the clean baseline collection
    try:
        client.delete_collection(COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    total_chunks = 0

    for file in sorted(DOCUMENTS_DIR.glob("*.txt")):
        print(f"\nProcessing: {file.name}")

        text = file.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks):
            # Generate embedding using Ollama
            response = ollama.embed(
                model=EMBEDDING_MODEL,
                input=chunk
            )

            embedding = response["embeddings"][0]

            # Store the chunk and its embedding
            collection.add(
                ids=[f"{file.stem}_{index}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": file.name,
                    "chunk_index": index,
                    "dataset": "clean"
                }]
            )

            total_chunks += 1

        print(f"  Stored {len(chunks)} chunks")

    print("\n-----------------------------")
    print("Ingestion completed")
    print(f"Documents: {len(list(DOCUMENTS_DIR.glob('*.txt')))}")
    print(f"Chunks: {total_chunks}")
    print(f"Database: {DATABASE_DIR}")
    print("-----------------------------")


if __name__ == "__main__":
    main()
