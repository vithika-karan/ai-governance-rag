import re
from pathlib import Path

import pymupdf


ARTICLE_HEADING_RE = re.compile(
    r"^Article\s+(\d+[a-z]?)\s*$",
    re.IGNORECASE,
)
PARAGRAPH_RE = re.compile(r"^(\d+)\.\s*$")
AMENDMENT_MARKER_RE = re.compile(r"^▼[BM]\d*(?:\s+_+)?$")
PAGE_HEADER_RE = re.compile(
    r"^\d{5}R\d{4}\s+—\s+EN\s+—\s+\d{2}\.\d{2}\.\d{4}"
    r"\s+—\s+\d{3}\.\d{3}\s+—\s+\d+$"
)


class EUAIActParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)

    def extract_pages(self) -> list[dict]:
        doc = pymupdf.open(self.pdf_path)
        pages = []

        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text")

            if text.strip():
                pages.append({"page": page_number, "text": text.strip()})

        doc.close()
        return pages

    def parse_articles(self) -> list[dict]:
        articles = []
        current_article = None

        for page in self.extract_pages():
            page_number = page["page"]
            lines = [line.strip() for line in page["text"].splitlines()]

            for line_index, line in enumerate(lines):
                match = ARTICLE_HEADING_RE.match(line)

                if match and self._is_article_heading(lines, line_index):
                    if current_article is not None:
                        articles.append(current_article)

                    current_article = {
                        "article": match.group(1),
                        "text": "",
                        "page_start": page_number,
                        "page_end": page_number,
                    }
                    continue

                if current_article is not None and line:
                    current_article["text"] += line + "\n"
                    current_article["page_end"] = page_number

        if current_article is not None:
            articles.append(current_article)

        return articles

    def parse_paragraphs(self) -> list[dict]:
        paragraphs = []
        current_article = None
        current_paragraph = None
        current_text = []
        paragraph_page_start = None
        paragraph_page_end = None

        def save_paragraph():
            nonlocal current_paragraph
            nonlocal current_text
            nonlocal paragraph_page_start
            nonlocal paragraph_page_end

            if current_article is None or current_paragraph is None:
                return

            text = "\n".join(current_text).strip()
            if text:
                paragraphs.append(
                    {
                        "article": current_article,
                        "paragraph": current_paragraph,
                        "text": text,
                        "page_start": paragraph_page_start,
                        "page_end": paragraph_page_end,
                    }
                )

            current_paragraph = None
            current_text = []
            paragraph_page_start = None
            paragraph_page_end = None

        for page in self.extract_pages():
            page_number = page["page"]
            lines = [line.strip() for line in page["text"].splitlines()]

            for line_index, line in enumerate(lines):
                if self._is_noise_line(line):
                    continue

                article_match = ARTICLE_HEADING_RE.match(line)
                if article_match and self._is_article_heading(lines, line_index):
                    save_paragraph()
                    current_article = article_match.group(1)
                    continue

                paragraph_match = PARAGRAPH_RE.match(line)
                if paragraph_match and current_article is not None:
                    save_paragraph()
                    current_paragraph = paragraph_match.group(1)
                    paragraph_page_start = page_number
                    paragraph_page_end = page_number
                    continue

                if current_article is not None and current_paragraph is not None:
                    current_text.append(line)
                    paragraph_page_end = page_number

        save_paragraph()
        return paragraphs

    @staticmethod
    def _is_noise_line(line: str) -> bool:
        return (
            not line
            or bool(AMENDMENT_MARKER_RE.match(line))
            or bool(PAGE_HEADER_RE.match(line))
        )

    @staticmethod
    def _is_article_heading(lines: list[str], line_index: int) -> bool:
        """Reject wrapped inline legal references that mimic article headings."""
        following_lines = lines[line_index + 1 :]
        next_line = next((line for line in following_lines if line), "")
        return bool(next_line) and not next_line.lower().startswith(("of ", "and "))
