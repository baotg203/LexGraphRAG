CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,

    document_code TEXT,
    title TEXT,
    version INT,

    effective_from DATE,
    effective_to DATE,

    source TEXT,
    category TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,

    document_id INTEGER
        REFERENCES documents(id)
        ON DELETE CASCADE,

    article_number TEXT,

    content TEXT NOT NULL,

    category TEXT,

    embedding VECTOR(1024)
);

CREATE TABLE IF NOT EXISTS legal_triples (
    id SERIAL PRIMARY KEY,

    chunk_id INTEGER
        REFERENCES document_chunks(id)
        ON DELETE CASCADE,

    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS article_hashes (
    id SERIAL PRIMARY KEY,

    document_code TEXT,
    article_number TEXT,

    content_hash TEXT NOT NULL,

    document_version INTEGER,

    effective_from DATE,
    effective_to DATE,

    chunk_id INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(
        document_code,
        article_number,
        content_hash
    )
);