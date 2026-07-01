class ChunkRepository:
    def __init__(self, cur):
        self.cur = cur

    def insert(self, chunk):
        self.cur.execute("""
            INSERT INTO document_chunks(
                document_id,
                article_number,
                content,
                category,
                embedding
            )
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id
        """,
        (
            chunk.document_id,
            chunk.article_number,
            chunk.content,
            chunk.category,
            chunk.embedding
        ))

        return self.cur.fetchone()[0]