class TripleRepository:
    def __init__(self, cur):
        self.cur = cur

    def get_by_chunk_id(
        self,
        chunk_id: int
    ) -> list[dict]:

        self.cur.execute("""
            SELECT
                subject,
                predicate,
                object
            FROM legal_triples
            WHERE chunk_id = %s
        """, (chunk_id,))

        rows = self.cur.fetchall()

        return [
            {
                "subject": r[0],
                "predicate": r[1],
                "object": r[2]
            }
            for r in rows
        ]

    def save(
        self,
        chunk_id: int,
        subject: str,
        predicate: str,
        obj: str
    ):
        self.cur.execute("""
            INSERT INTO legal_triples(
                chunk_id,
                subject,
                predicate,
                object
            )
            VALUES (%s,%s,%s,%s)
        """, (
            chunk_id,
            subject,
            predicate,
            obj
        ))

    def save_many(
        self,
        chunk_id: int,
        triples: list[dict]
    ):
        for t in triples:

            subject = t.get("subject")
            predicate = t.get("predicate")
            obj = t.get("object")

            if not (
                subject and
                predicate and
                obj
            ):
                continue

            self.save(
                chunk_id,
                subject,
                predicate,
                obj
            )

    def delete_by_chunk_id(
        self,
        chunk_id: int
    ):
        self.cur.execute("""
            DELETE
            FROM legal_triples
            WHERE chunk_id=%s
        """, (chunk_id,))