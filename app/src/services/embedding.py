from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_id: str, device: str, trust_remote_code: bool = False):
        self.model = SentenceTransformer(model_id, device=device, trust_remote_code=trust_remote_code)

    def embed_passage(
        self,
        text: str
    ) -> list[float]:
        """
        Sinh embedding cho document/chunk.
        """
        return self.model.encode(
            f"passage: {text}",
            normalize_embeddings=True
        ).tolist()

    def embed_query(
        self,
        query: str,
        normalize_embeddings: bool = True
    ) -> list[float]:
        """
        Sinh embedding cho query.
        """
        return self.model.encode(query, normalize_embeddings=normalize_embeddings).tolist()

    def embed_passages(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """
        Batch embedding cho nhiều chunk.
        """
        texts = [
            f"passage: {t}"
            for t in texts
        ]

        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist()

    def embed_queries(
        self,
        queries: list[str]
    ) -> list[list[float]]:
        """
        Batch embedding cho nhiều query.
        """
        queries = [
            f"query: {q}"
            for q in queries
        ]

        return self.model.encode(
            queries,
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist()