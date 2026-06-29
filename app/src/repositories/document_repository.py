class DocumentRepository:
    def __init__(self, cur):
        self.cur = cur

    def get_next_version(self, document_code):
        self.cur.execute("""
            SELECT COALESCE(MAX(version),0)+1
            FROM documents
            WHERE document_code=%s
        """, (document_code,))
        return self.cur.fetchone()[0]

    def insert(self, metadata, source):
        self.cur.execute("""
            INSERT INTO documents(
                document_code,
                title,
                version,
                effective_from,
                effective_to,
                source,
                category
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """,
        (
            metadata["document_code"],
            metadata["title"],
            metadata["version"],
            metadata["effective_from"],
            metadata["effective_to"],
            source,
            metadata["category"]
        ))

        return self.cur.fetchone()[0]