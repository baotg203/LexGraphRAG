from dataclasses import dataclass


@dataclass
class Chunk:
    document_id: int
    article_number: str
    content: str
    category: str
    embedding: list