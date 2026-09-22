from app.ingestion.parser import EUAIActParser
from app.ingestion.chunker import ParagraphChunker


PDF_PATH = "data/raw/eu_ai_act_2026-07-27.pdf"


def test_article_count():
    parser = EUAIActParser(PDF_PATH)

    articles = parser.parse_articles()

    assert len(articles) == 119


def test_article_50_exists():
    parser = EUAIActParser(PDF_PATH)

    articles = parser.parse_articles()

    article_50 = next(
        article
        for article in articles
        if article["article"] == "50"
    )

    assert "Transparency obligations" in article_50["text"]
    assert article_50["page_start"] == 59
    assert article_50["page_end"] == 60


def test_cross_reference_does_not_create_article():
    parser = EUAIActParser(PDF_PATH)

    articles = parser.parse_articles()
    article_numbers = [article["article"] for article in articles]

    assert len(article_numbers) == len(set(article_numbers))
    assert article_numbers.count("10") == 1


def test_article_50_paragraphs():
    parser = EUAIActParser(PDF_PATH)

    paragraphs = parser.parse_paragraphs()
    article_50 = [
        paragraph
        for paragraph in paragraphs
        if paragraph["article"] == "50"
    ]

    assert len(article_50) == 7
    assert [paragraph["paragraph"] for paragraph in article_50] == [
        "1", "2", "3", "4", "5", "6", "7"
    ]


def test_article_50_paragraph_4_spans_pages():
    parser = EUAIActParser(PDF_PATH)

    paragraphs = parser.parse_paragraphs()
    paragraph_4 = next(
        paragraph
        for paragraph in paragraphs
        if paragraph["article"] == "50"
        and paragraph["paragraph"] == "4"
    )

    assert paragraph_4["page_start"] == 59
    assert paragraph_4["page_end"] == 60


def test_amendment_markers_removed():
    parser = EUAIActParser(PDF_PATH)

    paragraphs = parser.parse_paragraphs()

    for paragraph in paragraphs:
        assert "▼B" not in paragraph["text"]
        assert "▼M1" not in paragraph["text"]


def test_short_paragraph_produces_one_chunk():
    paragraph = {
        "article": "50",
        "paragraph": "1",
        "text": "This is a short paragraph.",
        "page_start": 59,
        "page_end": 59,
    }
    chunker = ParagraphChunker(max_chars=4000)

    chunks = chunker.chunk_paragraph(
        paragraph,
        document_id="eu-ai-act",
        version_date="2026-07-27",
    )

    assert len(chunks) == 1
    assert chunks[0].article == "50"
    assert chunks[0].paragraph == "1"


def test_long_paragraph_is_split():
    paragraph = {
        "article": "50",
        "paragraph": "1",
        "text": "This is a sentence. " * 500,
        "page_start": 59,
        "page_end": 60,
    }
    chunker = ParagraphChunker(max_chars=500)

    chunks = chunker.chunk_paragraph(
        paragraph,
        document_id="eu-ai-act",
        version_date="2026-07-27",
    )

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.article == "50"
        assert chunk.paragraph == "1"
