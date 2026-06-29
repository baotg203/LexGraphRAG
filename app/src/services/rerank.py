class RerankService:
    def __init__(self, model):
        self.model = model

    def rerank(self, query, documents):
        # Implement the reranking logic here using the model
        # For example, you can use the model to score each document based on the query
        scores = []
        for doc in documents:
            score = self.model.score(query, doc)
            scores.append((doc, score))
        
        # Sort documents based on scores in descending order
        ranked_documents = sorted(scores, key=lambda x: x[1], reverse=True)
        
        # Return only the documents in ranked order
        return [doc for doc, score in ranked_documents]