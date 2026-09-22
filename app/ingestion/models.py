from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentSection:
    document_id: str
    section_type: str
    title: str
    text: str
    page_start: int
    page_end: int

    article: Optional[str] = None
    paragraph: Optional[str] = None
    recital: Optional[str] = None
    annex: Optional[str] = None

    metadata: dict = field(default_factory=dict)
