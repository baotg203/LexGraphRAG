from dataclasses import dataclass


@dataclass
class Document:
    document_code: str
    title: str
    version: int
    effective_from: str
    effective_to: str | None
    category: str