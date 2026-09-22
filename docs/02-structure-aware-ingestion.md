# Stage 2: Structure-Aware EU AI Act Ingestion

## Goal

Turn the consolidated EU AI Act PDF into a validated, provenance-preserving
JSONL corpus. This stage intentionally stops before Qdrant or retrieval: its
responsibility is to understand the legal document's structure accurately.

## Source

The document registry is [data/raw/manifest.json](../data/raw/manifest.json).
It identifies the source as the English EUR-Lex consolidated Regulation (EU)
2024/1689, version date `2026-07-27`, with document ID `eu-ai-act`.

## Pipeline implemented

```text
PDF (151 pages)
  -> page extraction
  -> article parsing (119 sections)
  -> paragraph parsing (550 paragraphs)
  -> paragraph-aware chunking (563 chunks)
  -> data/processed/eu_ai_act_chunks.jsonl
```

### Page extraction

PyMuPDF extracts text page by page. The parser keeps page numbers throughout
the structural pass so a later chunk can cite its legal location.

### Article parsing

Article headings are detected only when a line matches an article heading such
as `Article 50`. The parser supports letter-suffixed amendment articles, such
as `4a`, `60a`, and `75a` through `75d`.

### Paragraph parsing

Paragraph markers are standalone numeric lines such as `1.` and `2.`. The
parser operates on page-aware source lines rather than flattened article text,
so a paragraph continues correctly when it crosses a page boundary.

### Chunking

Paragraphs are the semantic unit. A paragraph at or below 4,000 characters
becomes one retrieval chunk. Longer paragraphs split on conservative sentence
boundaries, carrying up to 400 characters of whole-sentence overlap. Every
chunk retains document, article, paragraph, page, language, authority, and
version metadata.

The 4,000/400 settings are a baseline for later retrieval experiments, not a
claim that they are universally optimal.

## Challenges found and decisions made

This PDF is not treated as plain text. The parser was adjusted only after
inspecting the actual text PyMuPDF extracted. The examples below show why.

### 1. A legal reference can look like an article heading

On page 8, the PDF wraps a reference across lines like this:

```text
Article 10
of Directive (EU) 2016/680
```

A naïve rule such as “every line matching `Article <number>` starts a new
section” would treat that reference as a second Article 10. It would split the
current Article 3 definition in the wrong place and produce duplicate article
records.

**Decision:** a potential heading is checked against the following source line.
`Article 10` followed by `of Directive ...` is treated as a wrapped reference,
not a structural boundary. A real heading, such as the following, is retained:

```text
Article 50
Transparency obligations for providers and deployers of certain AI systems
```

### 2. The consolidated version contains more than Articles 1–113

The original numbering ends at Article 113, but this 2026 consolidated version
also contains inserted provisions. For example:

```text
Article 4a
Processing of special categories of personal data for bias detection and correction

Article 60a
Obligations of providers of high-risk AI systems...
```

Ignoring letter-suffixed identifiers would omit valid obligations from the
retrieval corpus. This is especially problematic in a governance RAG system,
where an answer should reflect the current consolidated text.

**Decision:** article identifiers accept a numeric part with an optional letter
suffix. The parser therefore produces 119 article sections: the original
1–113 sequence plus `4a`, `60a`, and `75a`–`75d`.

### 3. EUR-Lex amendment labels are not legal content

The extracted PDF includes revision labels between otherwise continuous text:

```text
▼B
02024R1689 — EN — 27.07.2026 — 001.001 — 60
▼M1 __________
```

If kept, these labels would be embedded along with the law. A retrieval result
could then contain opaque symbols and repeated page identifiers instead of only
the relevant legal language.

**Decision:** remove only the exact marker and page-header formats observed in
this source. The parser does not use a broad rule such as “delete every line
containing a dash”, which could accidentally remove meaningful text.

### 4. Paragraphs can cross a page without repeating their number

Article 50 paragraph 4 begins on page 59:

```text
4.
Deployers of an AI system that generates or manipulates image,
audio or video content constituting a deep fake, shall disclose...
```

It continues on page 60 without another `4.` marker:

```text
Deployers of an AI system that generates or manipulates text which is
published with the purpose of informing the public on matters of public interest...
5.
The information referred to in paragraphs 1 to 4 shall be provided...
```

A parser that resets at every page would truncate paragraph 4 or mislabel its
continuation. This would harm citations and could separate a legal obligation
from its exceptions.

**Decision:** retain the active article and paragraph while moving to the next
page. The paragraph is saved only when the next numbered paragraph marker is
found. As a result, Article 50 paragraph 4 correctly records pages 59–60.

## Validation

Run the pipeline from the repository root:

```bash
env/bin/python scripts/ingest_document.py
```

Expected result:

```text
Paragraphs: 550
Chunks: 563
Output: data/processed/eu_ai_act_chunks.jsonl
```

Run the test suite:

```bash
env/bin/python -m pytest -q
```

Current result:

```text
8 passed
```

The tests cover article count and uniqueness, Article 50 detection, exclusion
of amendment markers, Article 50's seven paragraphs, its page-59-to-60
paragraph-boundary case, and short/long paragraph chunk behavior.

## Result

The generated corpus is
[data/processed/eu_ai_act_chunks.jsonl](../data/processed/eu_ai_act_chunks.jsonl).
It contains one JSON object per line, for example:

```json
{
  "chunk_id": "eu-ai-act_article-50_p4",
  "text": "...",
  "metadata": {
    "document_id": "eu-ai-act",
    "section_type": "article",
    "article": "50",
    "paragraph": "4",
    "page_start": 59,
    "page_end": 60,
    "version_date": "2026-07-27",
    "language": "en",
    "authority": "European Union"
  }
}
```

## Explicit boundary

No documents have been indexed in Qdrant, and no retrieval, reranking, or LLM
answer-generation behavior exists yet. The next stage is a baseline dense RAG
retriever built against this fixed corpus.
