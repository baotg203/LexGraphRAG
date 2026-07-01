from sentence_transformers import CrossEncoder

RERANK_MODEL = CrossEncoder(
    "BAAI/bge-reranker-base",
    device='cpu'
)