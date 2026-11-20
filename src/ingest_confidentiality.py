
from pathlib import Path

import chromadb
import ollama

ROOT = Path(__file__).resolve().parents[1]

CLEAN_DIR = ROOT / "documents" / "confidentiality" / "clean"
POISONED_DIR = ROOT / "documents" / "confidentiality" / "poisoned"

EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "rag_documents"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text):
    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP

    for start in range(0, len(text), step):
        chunk = text[start:start + CHUNK_SIZE].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def build_database(database_dir, include_poisoned=False):
    client = chromadb.PersistentClient(path=str(database_dir))

    try:
        client.delete_collection(COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    files = [(file, "clean") for file in sorted(CLEAN_DIR.glob("*.txt"))]

    if include_poisoned:
        files += [
            (file, "poisoned")
            for file in sorted(POISONED_DIR.glob("*.txt"))
        ]

    total_chunks = 0

    for file, dataset in files:
        text = file.read_text(encoding="utf-8")

        for index, chunk in enumerate(chunk_text(text)):
            embedding = ollama.embed(
                model=EMBEDDING_MODEL,
                input=chunk
            )["embeddings"][0]

            collection.add(
                ids=[f"{dataset}_{file.stem}_{index}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": file.name,
                    "chunk_index": index,
                    "dataset": dataset,
                    "classification": (
                        "confidential"
                        if file.name == "hr_salary_records.txt"
                        else "internal"
                    )
                }]
            )

            total_chunks += 1

        print(f"  {dataset}: {file.name}")

    print(f"  Total chunks: {total_chunks}")
    print(f"  Database: {database_dir}")


def main():
    print("\nBuilding CLEAN confidentiality database")

    build_database(
        ROOT / "data" / "chroma_confidentiality_clean",
        include_poisoned=False
    )

    print("\nBuilding POISONED confidentiality database")

    build_database(
        ROOT / "data" / "chroma_confidentiality_poisoned",
        include_poisoned=True
    )


if __name__ == "__main__":
    main()
