# Stage 3: Baseline Dense Retrieval

## Goal

Create the simplest usable retrieval baseline against the fixed EU AI Act
corpus. The purpose is to establish a control system that later BM25, hybrid,
and reranking experiments can be compared against.

This stage deliberately includes only:

```text
Question -> BGE-M3 embedding -> Qdrant top-K vector search -> evidence chunks
```

It does not include an LLM, BM25, reciprocal-rank fusion, a cross-encoder, or
retrieval metrics.

## What was built

- `app/retrieval/embeddings.py` loads `BAAI/bge-m3` and returns normalized
  embeddings.
- `app/retrieval/vector_store.py` creates, upserts into, and queries a local
  Qdrant collection named `eu_ai_act`.
- `scripts/index_chunks.py` reads the versioned JSONL corpus, embeds each
  chunk, and inserts it into Qdrant.
- `scripts/test_retrieval.py` runs three representative legal queries and
  displays the retrieved article, paragraph, stable chunk ID, and score.

Qdrant runs locally in the Docker container `ai-governance-qdrant` at port
`6333`. Local infrastructure keeps this stage focused on the retrieval design
instead of cloud deployment.

## Indexing result

The BGE-M3 model produced a 1,024-dimensional vector for every chunk:

```text
Loaded 563 chunks
Embedding shape: (563, 1024)
Indexed 563 chunks
```

The first embedding run took about 14 minutes because the model weights had to
be downloaded and initialized. Subsequent query embeddings use the cached
model and complete quickly.

## Retrieval checks

The following manual smoke tests ran against the indexed collection with
`top_k = 5`.

| Question | Strongest observed evidence | Interpretation |
| --- | --- | --- |
| What AI practices are prohibited under the EU AI Act? | Article 5, paragraph 1 at rank 1 (score 0.7186). | The baseline retrieves the core prohibition provision. |
| What are the requirements for high-risk AI systems? | Articles 15, 8, 14, and 17 occupy the top five results. | The baseline retrieves relevant technical, governance, human-oversight, and quality-management requirements. |
| What are the transparency obligations for providers and deployers of certain AI systems? | Article 50, paragraphs 1 and 4 appear at ranks 4 and 5. | The target article is retrieved within top five, but it is not ranked first. This is useful baseline evidence, not a problem to hide or tune away before evaluation exists. |

For the transparency query, Article 13 ranked first. That provision also
contains transparency-related requirements for high-risk AI systems, which
explains the semantic match. Article 50 is nevertheless the more direct legal
source for the wording of this question. This distinction is exactly why the
next stage will introduce a labelled evaluation set instead of judging quality
from one query at a time.

## Important implementation detail: repeated article/paragraph labels

Some large paragraphs were split during ingestion. Their chunks retain the
same article and paragraph metadata but have different stable IDs, for example:

```text
eu-ai-act_article-5_p1
eu-ai-act_article-5_p1_c1
```

This explains why the prohibition query can show Article 5 paragraph 1 more
than once in the top results. It is not a duplicate database insert: the two
results are different sentence-bounded pieces of one long legal paragraph.
The retrieval script prints `chunk_id` so this distinction is visible.

## Compatibility decision

The installed Qdrant client version exposes `query_points(...).points` rather
than the older `search(...)` method. The vector-store wrapper uses the current
client API while keeping a simple `search(vector, limit)` method for the rest
of the application.

## How to run

Start Qdrant if it is not already running:

```bash
docker start ai-governance-qdrant
```

Create or refresh the dense index:

```bash
HF_HUB_DISABLE_XET=1 env/bin/python -u scripts/index_chunks.py
```

Inspect baseline retrieval:

```bash
env/bin/python scripts/test_retrieval.py
```

## Explicit boundary

The system can retrieve evidence only. It does not yet generate answers or
citations for users, and it has no evaluation dataset or retrieval metrics.
The next stage is to define a labelled retrieval evaluation set and measure
this dense baseline with Recall@K, Precision@K, MRR, and nDCG.
