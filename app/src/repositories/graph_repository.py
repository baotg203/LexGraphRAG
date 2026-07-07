from app.core.graph import neo4j_driver

class GraphRepository:
    def __init__(self, config):
        self.driver = neo4j_driver

    # =====================================================
    # CORE SESSION
    # =====================================================
    def close(self):
        self.driver.close()

    def run(self, query, **params):
        with self.driver.session() as session:
            return session.run(query, params)

    # =====================================================
    # MAIN INGEST ENTRY
    # =====================================================
    def save_legal_chunk(
        self,
        metadata: dict,
        chunk_id: str,
        article_no: str,
        content: str,
        triples: list
    ):
        """
        Version-aware graph ingestion with proper Cypher syntax.
        """
        query = """
        // =========================
        // LAW + VERSION
        // =========================
        MERGE (law:Law {document_code: $document_code})
        SET law.title = $title,
            law.category = $category

        MERGE (ver:LawVersion {
            document_code: $document_code,
            version: $version
        })
        SET ver.effective_from = date($effective_from),
            ver.effective_to = CASE WHEN $effective_to IS NULL THEN null ELSE date($effective_to) END,
            ver.is_active = $is_active,
            ver.ingested_at = datetime()

        MERGE (law)-[:HAS_VERSION]->(ver)

        // =========================
        // ARTICLE
        // =========================
        MERGE (art:Article {
            document_code: $document_code,
            version: $version,
            article_number: $article_no
        })
        SET art.content = $content,
            art.updated_at = datetime()

        MERGE (ver)-[:CONTAINS]->(art)

        // =========================
        // CHUNK
        // =========================
        MERGE (c:Chunk {chunk_id: $chunk_id})
        SET c.article_number = $article_no,
            c.version = $version

        MERGE (art)-[:HAS_CHUNK]->(c)

        // =========================
        // FACTS WITH VERSIONING
        // =========================
        WITH c, $triples AS triples, $version AS version

        UNWIND triples AS t

        // Create current fact + entities
        MERGE (new_f:LegalFact {
            subject: t.subject,
            predicate: t.predicate,
            object: t.object,
            version: version
        })

        MERGE (s:Entity {name: t.subject})
        MERGE (o:Entity {name: t.object})

        MERGE (s)-[:SUBJECT_OF]->(new_f)
        MERGE (new_f)-[:OBJECT_OF]->(o)
        MERGE (new_f)-[:SUPPORTED_BY]->(c)

        // =========================
        // VERSION LINKING LOGIC (fixed)
        // =========================
        WITH new_f, c, t, version

        OPTIONAL MATCH (old_f:LegalFact {
            subject: t.subject,
            predicate: t.predicate,
            object: t.object
        })
        WHERE old_f.version < version AND old_f <> new_f

        WITH new_f, old_f
        WHERE old_f IS NOT NULL

        MERGE (old_f)-[:SUPERSEDES]->(new_f)

        RETURN count(new_f) AS facts_created
        """

        self.run(
            query,
            document_code=metadata["document_code"],
            title=metadata["title"],
            category=metadata.get("category"),
            version=metadata["version"],
            effective_from=metadata["effective_from"],
            effective_to=metadata["effective_to"],
            is_active=metadata.get("effective_to") is None,
            article_no=article_no,
            content=content[:8000],
            chunk_id=str(chunk_id),
            triples=triples
        )

    # =====================================================
    # ENTITY OPERATIONS
    # =====================================================
    def merge_entity(self, name: str):
        query = """
        MERGE (e:Entity {name: $name})
        RETURN e
        """
        return self.run(query, name=name)

    # =====================================================
    # FACT SEARCH
    # =====================================================
    def find_facts_by_entity(self, entity: str):
        query = """
        MATCH (e:Entity {name: $entity})-[:SUBJECT_OF]->(f:LegalFact)
        RETURN f.subject, f.predicate, f.object, f.version
        """
        return self.run(query, entity=entity)

    # =====================================================
    # GET CONTEXT FOR RAG
    # =====================================================
    def get_supporting_chunks(self, subject: str):
        query = """
        MATCH (e:Entity {name: $subject})-[:SUBJECT_OF]->(f:LegalFact)
              -[:SUPPORTED_BY]->(c:Chunk)
        RETURN c.chunk_id, c.article_number, f.subject, f.predicate, f.object
        """
        return self.run(query, subject=subject)
    
    
    def retrieve_latest(
        self,
        category=None,
        law_code=None,
        top_k=8
    ):
        try:
            with self.driver.session() as session:

                category_condition = (
                    "AND law.category = $category"
                    if category else ""
                )

                result = session.run(
                    f"""
                    MATCH (law:Law)
                    WHERE (
                        $law_code IS NULL
                        OR law.document_code = $law_code
                    )
                    {category_condition}

                    MATCH (law)-[:HAS_VERSION]->(ver:LawVersion)
                    MATCH (ver)-[:CONTAINS]->(art:Article)
                    MATCH (art)-[:HAS_CHUNK]->(c:Chunk)

                    RETURN
                        c.chunk_id AS chunk_id,
                        c.content AS content,
                        art.article_number AS article_number,
                        art.content AS article_content,
                        law.title AS title,
                        law.document_code AS document_code,
                        ver.version AS version

                    ORDER BY ver.version DESC
                    LIMIT $top_k
                    """,
                    category=category,
                    law_code=law_code,
                    top_k=top_k
                )

                return [r.data() for r in result]

        except Exception as e:
            print(f"Neo4j error: {e}")
            return []
        
    def expand_chunk(self, chunk_id):
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (c:Chunk)
                    WHERE c.chunk_id = $chunk_id

                    MATCH (art:Article)-[:HAS_CHUNK]->(c)
                    MATCH (ver:LawVersion)-[:CONTAINS]->(art)
                    MATCH (law:Law)-[:HAS_VERSION]->(ver)

                    OPTIONAL MATCH (art)-[:HAS_CHUNK]->(c2:Chunk)

                    RETURN
                        c2.chunk_id AS chunk_id,
                        c2.content AS content,
                        art.content AS article_content,
                        law.title AS law_title,
                        ver.version AS version,
                        law.document_code AS document_code
                    """,
                    chunk_id=str(chunk_id)
                )

                return [r.data() for r in result]

        except Exception as e:
            print(f"Neo4j expand error: {e}")
            return []
        
    def get_chunk_relationships(self, chunk_id):
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (c:Chunk {chunk_id: $chunk_id})
                        <-[:SUPPORTED_BY]-
                        (f:LegalFact)

                    OPTIONAL MATCH (s:Entity)-[:SUBJECT_OF]->(f)
                    OPTIONAL MATCH (f)-[:OBJECT_OF]->(o:Entity)

                    RETURN
                        f.subject AS subject,
                        f.predicate AS predicate,
                        f.object AS object,
                        s.name AS subject_entity,
                        o.name AS object_entity
                    """,
                    chunk_id=str(chunk_id)
                )

                return [record.data() for record in result]

        except Exception as e:
            print(f"Neo4j relationship error: {e}")
            return []