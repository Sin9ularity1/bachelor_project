
from pathlib import Path

import chromadb
import ollama

# Project paths
ROOT = Path(__file__).resolve().parents[1]
CLEAN_DOCUMENTS_DIR = ROOT / "documents" / "clean"
POISONED_DOCUMENTS_DIR = ROOT / "documents" / "poisoned"
DATABASE_DIR = ROOT / "data" / "chroma_poisoned"

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

    # Rebuild the experimental collection
    try:
        client.delete_collection(COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    total_chunks = 0

    document_files = (
        [(file, "clean") for file in sorted(CLEAN_DOCUMENTS_DIR.glob("*.txt"))]
        + [(file, "poisoned") for file in sorted(POISONED_DOCUMENTS_DIR.glob("*.txt"))]
    )

    for file, dataset in document_files:
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
                ids=[f"{dataset}_{file.stem}_{index}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": file.name,
                    "chunk_index": index,
                    "dataset": dataset
                }]
            )

            total_chunks += 1

        print(f"  Stored {len(chunks)} chunks")

    print("\n-----------------------------")
    print("Ingestion completed")
    print(f"Clean documents: {len(list(CLEAN_DOCUMENTS_DIR.glob('*.txt')))}")
    print(f"Poisoned documents: {len(list(POISONED_DOCUMENTS_DIR.glob('*.txt')))}")
    print(f"Chunks: {total_chunks}")
    print(f"Database: {DATABASE_DIR}")
    print("-----------------------------")


if __name__ == "__main__":
    main()
