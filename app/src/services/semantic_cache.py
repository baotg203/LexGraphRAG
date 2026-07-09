class SemanticCacheService:


    def __init__(
        self,
        repository,
        embedding_service
    ):
        self.repository = repository
        self.embedding_service = embedding_service



    def get(
        self,
        question,
        context_signature,
        threshold=0.9
    ):

        embedding = (
            self.embedding_service
            .embed_query(question)
        )


        results = (
            self.repository
            .search(
                embedding
            )
        )

        for item in results:

            similarity = (
                1 -
                item["score"]
            )


            if similarity < threshold:
                continue


            if (
                item["context_signature"]
                !=
                context_signature
            ):
                continue


            return item


        return None



    def save(
        self,
        question,
        context_signature,
        answer,
        chunk_ids
    ):

        embedding = self.embedding_service.embed_query(
            question
        )

        self.repository.save(
            embedding,
            context_signature,
            answer,
            chunk_ids
        )