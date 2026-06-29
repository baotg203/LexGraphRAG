class HashRepository:
    def __init__(self, cur):
        self.cur = cur

    def exists(
        self,
        document_code,
        article_no,
        content_hash
    ):
        self.cur.execute("""
            SELECT id
            FROM article_hashes
            WHERE
                document_code=%s
                AND article_number=%s
                AND content_hash=%s
        """,
        (
            document_code,
            article_no,
            content_hash
        ))

        return self.cur.fetchone() is not None

    def save(self, values):
        self.cur.execute("""
            INSERT INTO article_hashes(
                document_code,
                article_number,
                content_hash,
                document_version,
                effective_from,
                effective_to,
                chunk_id
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s
            )
        """, values)