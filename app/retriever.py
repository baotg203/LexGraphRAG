import psycopg2
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import re
from config import NEO4J_CONFIG, DB_CONFIG

neo4j_driver = GraphDatabase.driver(
    NEO4J_CONFIG["uri"],
    auth=(
        NEO4J_CONFIG["user"],
        NEO4J_CONFIG["password"]
    )
)

model = SentenceTransformer(
    "intfloat/multilingual-e5-base",
    device="cpu"
)

# =========================
# RETRIEVE
# =========================

def retrieve_pgvector(
    question: str,
    top_k: int = 5,
    document_id: int | None = None
):

    q_emb = model.encode(
        f"query: {question}",
        normalize_embeddings=True
    ).tolist()

    sql = """
    SELECT
        dc.id,
        dc.document_id,
        dc.article_number,
        dc.content,
        1 - (dc.embedding <=> %s::vector) AS similarity
    FROM document_chunks dc
    """

    params = [q_emb]

    if document_id is not None:
        sql += """
        WHERE dc.document_id = %s
        """
        params.append(document_id)

    sql += """
    ORDER BY dc.embedding <=> %s::vector
    LIMIT %s
    """

    params.extend([q_emb, top_k])

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:

            cur.execute(sql, params)

            rows = cur.fetchall()

    return [
        {
            "chunk_id": row[0],
            "document_id": row[1],
            "article_number": row[2],
            "content": row[3],
            "similarity": float(row[4])
        }
        for row in rows
    ]

def extract_keywords(question):
    return [
        x.strip()
        for x in re.findall(
            r"[A-Za-zÀ-ỹ0-9\s]+",
            question
        )
        if len(x.strip()) > 2
    ]

def retrieve_graph_from_chunks(
    chunk_ids,
    limit=50
):

    cypher = """
    MATCH (c:Chunk)<-[:SUPPORTED_BY]-(f:LegalFact)

    WHERE c.chunk_id IN $chunk_ids

    RETURN
        f.subject AS subject,
        f.predicate AS predicate,
        f.object AS object,
        c.chunk_id AS chunk_id,
        c.article_number AS article_number,
        c.document_title AS document_title

    LIMIT $limit
    """

    with neo4j_driver.session() as session:

        result = session.run(
            cypher,
            chunk_ids=chunk_ids,
            limit=limit
        )

        return [dict(r) for r in result]

def retrieve(
    question,
    top_k_vector=5,
    top_k_graph=50
):
    # ===== Step 1: Vector Retrieval =====

    vector_chunks = retrieve_pgvector(
        question,
        top_k=top_k_vector
    )

    if not vector_chunks:
        return {
            "chunks": [],
            "facts": []
        }

    # ===== Step 2: lấy chunk ids =====

    chunk_ids = [
        c["chunk_id"]
        for c in vector_chunks
    ]

    # ===== Step 3: Graph Expansion =====

    graph_facts = retrieve_graph_from_chunks(
        chunk_ids,
        limit=top_k_graph
    )

    return {
        "chunks": vector_chunks,
        "facts": graph_facts
    }

# =========================
# CONTEXT
# =========================

def build_context(
    chunks,
    facts
):

    contexts = []

    contexts.append(
        "=== VECTOR RETRIEVAL ==="
    )

    for chunk in chunks:

        contexts.append(
            f"""
[ARTICLE {chunk['article_number']}]

{chunk['content']}
"""
        )

    contexts.append(
        "\n=== KNOWLEDGE GRAPH ==="
    )

    for fact in facts:

        contexts.append(
            f"""
{fact['subject']}
--[{fact['predicate']}]-->
{fact['object']}

Điều:
{fact['article_number']}

Văn bản:
{fact['document_title']}
"""
        )

    return "\n".join(contexts)