# Project Build Log

This folder records the project stage by stage: the objective, implementation,
validation evidence, problems discovered, and decisions made. It is intended to
make the portfolio's engineering process as inspectable as its final result.

## Completed stages

| Stage | Status | Record |
| --- | --- | --- |
| 1. Project foundation | Complete | [01-project-foundation.md](01-project-foundation.md) |
| 2. Structure-aware ingestion | Complete | [02-structure-aware-ingestion.md](02-structure-aware-ingestion.md) |
| 3. Baseline dense retrieval | Complete | [03-baseline-dense-retrieval.md](03-baseline-dense-retrieval.md) |

## Current pipeline boundary

The processed corpus is ready for retrieval work:

```text
EU AI Act PDF -> pages -> articles -> paragraphs -> retrieval chunks -> JSONL
  -> BGE-M3 embeddings -> Qdrant dense search
```

Dense indexing and retrieval are available. Evaluation, hybrid retrieval,
reranking, and answer generation have not yet been built.

## Documentation convention for future stages

Each new stage record should include:

1. Goal and scope.
2. What was built or changed.
3. Validation commands and results.
4. Problems or source-specific edge cases found.
5. The decision taken and why.
6. The resulting state and explicit next boundary.
