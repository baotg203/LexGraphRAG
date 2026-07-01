from psycopg2.extras import RealDictCursor

class VectorRepository:
    def __init__(
        self,
        db,
        embedding_model
    ):
        self.db = db
        self.embedding_model = embedding_model

    def semantic_search(
        self,
        query: str,
        category: str = None,
        top_k: int = 10,
        prefer_latest: bool = True
    ):
        embedding = self.embedding_model.embed_query(query)

        conn = self.db

        try:
            cur = conn.cursor(
                cursor_factory=RealDictCursor
            )

            category_condition = ""
            params = [embedding]

            if category:
                category_condition = "AND d.category = %s"
                params.append(category)

            params.append(
                top_k * 2 if prefer_latest else top_k
            )

            if prefer_latest:
                sql = f"""
                SELECT
                    dc.id as chunk_id,
                    dc.content,
                    d.title,
                    d.version,
                    d.effective_from,
                    d.effective_to,
                    d.document_code,
                    (1 - (
                        dc.embedding <=> %s::vector
                    )) as similarity
                FROM document_chunks dc
                JOIN documents d
                    ON dc.document_id = d.id
                WHERE 1=1
                    {category_condition}
                ORDER BY
                    similarity DESC,
                    CASE
                        WHEN d.effective_to IS NULL
                        THEN 1000
                        ELSE 0
                    END DESC,
                    d.version DESC
                LIMIT %s
                """
            else:
                sql = f"""
                SELECT
                    dc.id as chunk_id,
                    dc.content,
                    d.title,
                    d.version,
                    d.effective_from,
                    d.effective_to,
                    d.document_code,
                    (1 - (
                        dc.embedding <=> %s::vector
                    )) as similarity
                FROM document_chunks dc
                JOIN documents d
                    ON dc.document_id = d.id
                WHERE 1=1
                    {category_condition}
                ORDER BY similarity DESC
                LIMIT %s
                """

            cur.execute(sql, params)

            return [
                dict(r)
                for r in cur.fetchall()
            ]

        finally:
            cur.close()