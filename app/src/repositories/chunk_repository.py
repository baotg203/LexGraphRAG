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
    
    def get_all_chunks(self):
        self.cur.execute("""
            SELECT id, content
            FROM document_chunks
            ORDER BY id
        """)
        return self.cur.fetchall()

    def update_embedding(self, chunk_id, embedding):
        self.cur.execute("""
            UPDATE document_chunks
            SET embedding = %s
            WHERE id = %s
        """, (embedding, chunk_id))