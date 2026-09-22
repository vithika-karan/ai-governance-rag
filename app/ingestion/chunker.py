import re
from dataclasses import dataclass


@dataclass
class RetrievalChunk:
    chunk_id: str
    text: str
    document_id: str
    section_type: str
    article: str
    paragraph: str
    page_start: int
    page_end: int
    version_date: str
    language: str = "en"
    authority: str = "European Union"


class ParagraphChunker:
    def __init__(self, max_chars: int = 4000, overlap_chars: int = 400):
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def chunk_paragraph(
        self,
        paragraph: dict,
        document_id: str,
        version_date: str,
    ) -> list[RetrievalChunk]:
        text = paragraph["text"].strip()

        if len(text) <= self.max_chars:
            return [
                self._create_chunk(
                    paragraph=paragraph,
                    text=text,
                    document_id=document_id,
                    version_date=version_date,
                    chunk_index=0,
                )
            ]

        return self._split_long_paragraph(
            paragraph=paragraph,
            document_id=document_id,
            version_date=version_date,
        )

    def _create_chunk(
        self,
        paragraph: dict,
        text: str,
        document_id: str,
        version_date: str,
        chunk_index: int,
    ) -> RetrievalChunk:
        article = paragraph["article"]
        paragraph_number = paragraph["paragraph"]
        suffix = "" if chunk_index == 0 else f"_c{chunk_index}"
        chunk_id = f"{document_id}_article-{article}_p{paragraph_number}{suffix}"

        return RetrievalChunk(
            chunk_id=chunk_id,
            text=text,
            document_id=document_id,
            section_type="article",
            article=article,
            paragraph=paragraph_number,
            page_start=paragraph["page_start"],
            page_end=paragraph["page_end"],
            version_date=version_date,
        )

    def _split_long_paragraph(
        self,
        paragraph: dict,
        document_id: str,
        version_date: str,
    ) -> list[RetrievalChunk]:
        sentences = self._split_sentences(paragraph["text"].strip())
        chunks = []
        current_sentences = []
        current_length = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if (
                current_sentences
                and current_length + sentence_length + 1 > self.max_chars
            ):
                chunks.append(
                    self._create_chunk(
                        paragraph=paragraph,
                        text=" ".join(current_sentences),
                        document_id=document_id,
                        version_date=version_date,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1

                current_sentences = self._get_overlap_sentences(current_sentences)
                current_length = sum(len(item) for item in current_sentences)

            current_sentences.append(sentence)
            current_length += sentence_length + 1

        if current_sentences:
            chunks.append(
                self._create_chunk(
                    paragraph=paragraph,
                    text=" ".join(current_sentences),
                    document_id=document_id,
                    version_date=version_date,
                    chunk_index=chunk_index,
                )
            )

        return chunks

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
            if sentence.strip()
        ]

    def _get_overlap_sentences(self, sentences: list[str]) -> list[str]:
        overlap = []
        length = 0

        for sentence in reversed(sentences):
            if length + len(sentence) > self.overlap_chars:
                break

            overlap.insert(0, sentence)
            length += len(sentence)

        return overlap


def chunk_to_dict(chunk: RetrievalChunk) -> dict:
    return {
        "chunk_id": chunk.chunk_id,
        "text": chunk.text,
        "metadata": {
            "document_id": chunk.document_id,
            "section_type": chunk.section_type,
            "article": chunk.article,
            "paragraph": chunk.paragraph,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "version_date": chunk.version_date,
            "language": chunk.language,
            "authority": chunk.authority,
        },
    }
