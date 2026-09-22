import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.parser import EUAIActParser
from app.ingestion.chunker import ParagraphChunker, chunk_to_dict


PDF_PATH = "data/raw/eu_ai_act_2026-07-27.pdf"
OUTPUT_PATH = "data/processed/eu_ai_act_chunks.jsonl"
DOCUMENT_ID = "eu-ai-act"
VERSION_DATE = "2026-07-27"


def main():
    parser = EUAIActParser(PDF_PATH)
    paragraphs = parser.parse_paragraphs()
    chunker = ParagraphChunker(max_chars=4000, overlap_chars=400)

    chunks = []
    for paragraph in paragraphs:
        chunks.extend(
            chunker.chunk_paragraph(
                paragraph=paragraph,
                document_id=DOCUMENT_ID,
                version_date=VERSION_DATE,
            )
        )

    output_path = Path(OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk_to_dict(chunk), ensure_ascii=False) + "\n")

    print(f"Paragraphs: {len(paragraphs)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
