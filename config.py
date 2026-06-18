# =====================================================

# CONFIG

# =====================================================
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "law_chatbot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

NEO4J_CONFIG = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "user": os.getenv("NEO4J_USER", "neo4j"),
    "password": os.getenv("NEO4J_PASSWORD", "password")
}

OLLAMA_CONFIG = {
    "host": os.getenv("OLLAMA_HOST", "localhost"),
    "uri": os.getenv("OLLAMA_URI", "http://localhost"),
    "port": int(os.getenv("OLLAMA_PORT", 11434)),
    "model": os.getenv("OLLAMA_MODEL", "llama2")
}

PDF_FOLDER = "data_test"
THRESHOLD_SIMILARITY = 0.85