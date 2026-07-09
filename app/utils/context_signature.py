import hashlib

class ContextSignature:

    @staticmethod
    def build(results: list[dict]) -> str:
        """
        Sinh signature từ đúng context truyền vào LLM.
        """

        fingerprints = []

        for r in results:

            fingerprints.append(
                "|".join([
                    str(r["document_code"]),
                    str(r["version"]),
                    str(r["article_number"]),
                    str(r["content_hash"])
                ])
            )

        fingerprints.sort()

        raw = "\n".join(fingerprints)

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()