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

        cur = None

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
                    dc.id AS chunk_id,
                    dc.content,
                    dc.article_number,

                    d.id AS document_id,
                    d.document_code,
                    d.title,
                    d.version,
                    d.effective_from,
                    d.effective_to,

                    ah.content_hash,

                    (
                        1 - (
                            dc.embedding <=> %s::vector
                        )
                    ) AS similarity

                FROM document_chunks dc

                JOIN documents d
                    ON dc.document_id = d.id

                LEFT JOIN article_hashes ah
                    ON ah.chunk_id = dc.id
                    AND ah.document_version = d.version

                WHERE 1 = 1
                    {category_condition}

                ORDER BY

                    similarity DESC,

                    CASE
                        WHEN d.effective_to IS NULL
                        THEN 1
                        ELSE 0
                    END DESC,

                    d.version DESC

                LIMIT %s
                """

            else:

                sql = f"""
                SELECT
                    dc.id AS chunk_id,
                    dc.content,
                    dc.article_number,

                    d.id AS document_id,
                    d.document_code,
                    d.title,
                    d.version,
                    d.effective_from,
                    d.effective_to,

                    ah.content_hash,

                    (
                        1 - (
                            dc.embedding <=> %s::vector
                        )
                    ) AS similarity

                FROM document_chunks dc

                JOIN documents d
                    ON dc.document_id = d.id

                LEFT JOIN article_hashes ah
                    ON ah.chunk_id = dc.id
                    AND ah.document_version = d.version

                WHERE 1 = 1
                    {category_condition}

                ORDER BY similarity DESC

                LIMIT %s
                """

            cur.execute(sql, params)

            return [
                dict(row)
                for row in cur.fetchall()
            ]

        finally:
            if cur:
                cur.close()