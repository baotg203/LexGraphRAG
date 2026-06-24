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

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-username/LexGraphRAG.git
cd LexGraphRAG
```

### 2. Create Environment File

Create a `.env` file in the project root:

```env
DB_HOST=psql_host
DB_PORT=psql_port
DB_NAME=psql_name
DB_USER=psql_user
DB_PASSWORD=lsql_pass

NEO4J_URI=bolt://neo4j_host:7687
NEO4J_USER=neo4j_user
NEO4J_PASSWORD=neo4j_pass

OLLAMA_HOST=http://ollama_host
OLLAMA_PORT=ollama_port
OLLAMA_MODEL=ollama_model
```

### 3. Configure Deployment Environment

#### Docker Deployment

```bash
docker compose up -d --build
```

#### Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Start required services:

* PostgreSQL + PGVector
* Neo4j
* Ollama

Then run:

```bash
python app/main.py
```

### 4. Data Migration

After the services are running, ingest legal documents into the databases:

```bash
python ingest_pdf.py
```

This step will:

* Extract legal document content
* Generate embeddings
* Store vectors in PostgreSQL (PGVector)
* Create entities and relationships in Neo4j

### 5. Start Asking Questions

API endpoint:

```text
POST /chat
```

Example request:

```json
{
  "question": "Nam bao nhiêu tuổi thì được kết hôn?"
}
```
