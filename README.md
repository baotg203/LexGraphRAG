# LexGraphRAG
LexGraphRAG is an AI-powered legal assistant designed to support Vietnamese law retrieval, reasoning, and question answering. The system combines Graph Retrieval-Augmented Generation (GraphRAG), vector search, and large language models to provide accurate and explainable legal responses based on Vietnamese legal documents.

## Features
⚖️ Legal Question Answering for Vietnamese laws and regulations
🔍 Hybrid Retrieval using:
PostgreSQL + PGVector for semantic search
Neo4j Knowledge Graph for relationship-based retrieval
🤖 Local LLM inference with Ollama and Qwen models
📝 Retrieval-Augmented Generation (RAG)
🌐 FastAPI backend for API services
📚 Legal document chunking and indexing pipeline

## Architecture
User Query
     │
     ▼
 Query Processing
     │
     ├── Vector Retrieval (PGVector)
     │
     ├── Graph Retrieval (Neo4j)
     │
     ▼
 Context Fusion
     │
     ▼
 Qwen (Ollama)
     │
     ▼
 Legal Answer