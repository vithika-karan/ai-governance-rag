# Stage 1: Project Foundation

## Goal

Create a clean, production-oriented repository layout before implementing RAG
logic. The intended design separates API, ingestion, retrieval, generation,
evaluation, data, tests, scripts, notebooks, and results from the start.

## What was created

```text
app/
  api/ ingestion/ retrieval/ generation/ evaluation/ core/
data/
  raw/ processed/ evaluation/
tests/ scripts/ notebooks/ results/
```

The repository also contains `README.md`, `.gitignore`, `.env.example`,
`requirements.txt`, and `Dockerfile`. Empty directories use `.gitkeep` so the
layout is visible in Git.

## Dependency baseline

The environment pins the direct project dependencies in `requirements.txt`.
They cover the API surface, configuration, PDF parsing, embeddings, vector
storage client, lexical-retrieval baseline, Azure OpenAI integration, and test
runner.

For Azure OpenAI API-key authentication, the official Python `openai` SDK is
installed. Microsoft Entra ID support is deliberately deferred; it would add
`azure-identity` only if that authentication model is selected.

## Decisions

- Dependencies are pinned to versions installed in the project virtual
  environment to make the build reproducible.
- Secrets are not stored in the repository; environment configuration belongs
  in a local `.env` file derived from `.env.example` when credentials are added.
- No application code was added during this stage.

## Result

The project has a stable directory contract and a dedicated virtual environment.
The next stage can implement ingestion without coupling it to a vector database
or an LLM provider.
