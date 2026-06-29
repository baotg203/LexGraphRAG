from dataclasses import dataclass

@dataclass
class HashRecord:
    document_code: str
    article_number: str
    clause_number: str | None
    point_number: str | None
    content_hash: str
    document_version: int
    chunk_id: int