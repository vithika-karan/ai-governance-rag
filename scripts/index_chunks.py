import json
from pathlib import Path
import sys

from qdrant_client.models import PointStruct

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.vector_store import QdrantVectorStore


CHUNKS_PATH = "data/processed/eu_ai_act_chunks.jsonl"


def load_chunks() -> list[dict]:
    with Path(CHUNKS_PATH).open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main():
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    embedding_model = EmbeddingModel()
    embeddings = embedding_model.encode([chunk["text"] for chunk in chunks])
    print(f"Embedding shape: {embeddings.shape}")

    vector_store = QdrantVectorStore()
    vector_store.create_collection(vector_size=embeddings.shape[1])

    points = [
        PointStruct(
            id=index,
            vector=embedding.tolist(),
            payload=chunk,
        )
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    vector_store.upsert(points)
    print(f"Indexed {len(points)} chunks")


if __name__ == "__main__":
    main()
