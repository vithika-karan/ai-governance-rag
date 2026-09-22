# AI Governance RAG

Evaluation-driven Retrieval-Augmented Generation (RAG) system
for EU AI Act and AI governance documents.

## Objective

Build a reliable RAG system that can retrieve relevant regulatory
evidence, answer questions using that evidence, and provide
article-level citations.

The system will be evaluated on retrieval quality, answer quality,
citation grounding, and abstention behavior.

## Scope

Initial corpus:
- EU AI Act — Regulation (EU) 2024/1689
- Official European Commission AI Act guidance

## Planned Architecture

Documents
    ↓
Structure-aware ingestion
    ↓
Chunking + metadata
    ↓
Retrieval
    ↓
Reranking / ranking experiments
    ↓
LLM generation
    ↓
Citation grounding
    ↓
Evaluation

## Evaluation

The system will be evaluated using:
- AI Act Evaluation Benchmark
- Custom evaluation set
- Retrieval metrics
- Answer quality
- Citation grounding
- Abstention accuracy

## Status

🚧 In Progress