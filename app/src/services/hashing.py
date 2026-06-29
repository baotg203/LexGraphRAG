import hashlib
import re


class HashingService:
    def __init__(self, hash_repo):
        self.hash_repo = hash_repo

    @staticmethod
    def compute_hash(text):
        text = re.sub(
            r"\s+",
            " ",
            text.strip()
        )

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def is_changed(
        self,
        document_code,
        article_no,
        text
    ):
        h = self.compute_hash(text)

        return not self.hash_repo.exists(
            document_code,
            article_no,
            h
        )
    
    def hash_text(self, text):
        return self.compute_hash(text)

    def save_hash_record(
        self,
        document_code,
        article_no,
        text,
        version,
        effective_from,
        effective_to,
        chunk_id
    ):
        h = self.compute_hash(text)

        self.hash_repo.save(
            (
                document_code,
                article_no,
                h,
                version,
                effective_from,
                effective_to,
                chunk_id
            )
        )