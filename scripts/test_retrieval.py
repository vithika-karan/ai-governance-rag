from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.retrieval.embeddings import EmbeddingModel
from app.retrieval.vector_store import QdrantVectorStore


QUERIES = [
    "What are the transparency obligations for providers and deployers of certain AI systems?",
    "What AI practices are prohibited under the EU AI Act?",
    "What are the requirements for high-risk AI systems?",
]


def main():
    embedding_model = EmbeddingModel()
    vector_store = QdrantVectorStore()

    for query in QUERIES:
        vector = embedding_model.encode([query])[0].tolist()
        results = vector_store.search(vector, limit=5)

        print("\n" + "=" * 80)
        print(f"Query: {query}")
        for rank, result in enumerate(results, start=1):
            metadata = result.payload["metadata"]
            print(
                f"Rank {rank}: {result.payload['chunk_id']} — "
                f"Article {metadata['article']}, "
                f"Paragraph {metadata['paragraph']}, Score: {result.score:.4f}"
            )


if __name__ == "__main__":
    main()
