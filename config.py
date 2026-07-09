# =====================================================

# CONFIG

# =====================================================
import os
import torch

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5433),
    "dbname": os.getenv("DB_NAME", "legal_rag"),
    "user": os.getenv("DB_USER", "legal"),
    "password": os.getenv("DB_PASSWORD", "legalpass")
}

NEO4J_CONFIG = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "user": os.getenv("NEO4J_USER", "neo4j"),
    "password": os.getenv("NEO4J_PASSWORD", "password123")
}

OLLAMA_CONFIG = {
    "host": os.getenv("OLLAMA_HOST", "localhost"),
    "uri": os.getenv("OLLAMA_URI", "http://localhost"),
    "port": int(os.getenv("OLLAMA_PORT", 11434)),
    "model": os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct")
}

REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "db": int(os.getenv("REDIS_DB", 0)),
    "password": os.getenv("REDIS_PASSWORD", None),
    "session_ttl": int(os.getenv("REDIS_SESSION_TTL", 86400)),  # Time-to-live for session data in seconds
    "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", 3))  # Maximum number of connections in the pool
}

DEVICE = os.getenv("DEVICE", torch.device("cuda" if torch.cuda.is_available() else "cpu"))

PDF_FOLDER = 'data'

PDF_TEST = {
    "datdai2014" : {
        "document_code": "45/2013/QH13",
        "title": "Luật Đất đai",
        "effective_from": "2014-07-01",
        "effective_to": "2024-07-31",
        "category": "DATDAI"
    },
    "datdai2024": {
        "document_code": "31/2024/QH15",
        "title": "Luật Đất đai",
        "effective_from": "2024-08-01",
        "effective_to": None,
        "category": "DATDAI"
    },
    # "doanhnghiep2020": {
    #     "document_code": "59/2020/QH14",
    #     "title": "Luật Doanh nghiệp",
    #     "effective_from": "2021-01-01",
    #     "effective_to": "2024-12-31",
    #     "category": "DOANHNGHIEP"
    # },
    # "doanhnghiep2020tiep": {
    #     "document_code": "59/2020/QH14",
    #     "title": "Luật Doanh nghiệp",
    #     "effective_from": "2021-01-01",
    #     "effective_to": "2024-12-31",
    #     "category": "DOANHNGHIEP"
    # },
    # "doanhnghiep2025": {
    #     "document_code": "76/2025/QH15",
    #     "title": "Luật Doanh nghiệp",
    #     "effective_from": "2025-01-01",
    #     "effective_to": None,
    #     "category": "DOANHNGHIEP"
    # },
    "honnhan2014": {
        "document_code": "52/2014/QH13",
        "title": "Luật Hôn nhân và Gia đình",
        "effective_from": "2015-01-01",
        "effective_to": None,
        "category": "HONNHAN"
    }
}

THRESHOLD_SIMILARITY = 0.5