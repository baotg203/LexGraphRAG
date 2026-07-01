class RerankService:
    def __init__(self, model):
        self.model = model

    def rerank(self, query, results, top_k=5):
        if not results:
            return []
        
        pairs = [(query, result["content"]) for result in results]

        scores = self.model.predict(pairs)

        rerank = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True
        )

        if top_k:
            rerank = rerank[:top_k]

        return [
            {
                **result,
                "rerank_score": float(score)
            }
            for result, score in rerank
        ]