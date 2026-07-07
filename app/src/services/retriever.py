# app/services/retriever_service.py

from config import THRESHOLD_SIMILARITY


class RetrieverService:
    def __init__(
        self,
        vector_repository,
        graph_repository,
        rerank_service=None
    ):
        self.vector_repository = vector_repository
        self.graph_repository = graph_repository
        self.rerank_service = rerank_service

    def retrieve(
        self,
        query,
        category=None,
        top_k=10,
        use_llm_rerank=False,
        rerank_top_k=3
    ):
        # =========================
        # 1. VECTOR RETRIEVAL
        # =========================
        results = self.vector_repository.semantic_search(
            query=query,
            category=category,
            top_k=top_k
        )

        # =========================
        # 2. DEDUPLICATE
        # =========================
        seen = set()
        dedup_results = []

        for row in results:
            cid = (
                row.get("chunk_id")
                or row.get("id")
                or row.get("content")
            )

            if cid in seen:
                continue

            seen.add(cid)
            row["source"] = "postgres"
            dedup_results.append(row)

        results = dedup_results

        # =========================
        # 3. OPTIONAL RERANK
        # =========================
        if (
            use_llm_rerank
            and self.rerank_service
            and len(results) > 3
        ):
            results = self.rerank_service.rerank(
                query=query,
                results=results,
                top_k=rerank_top_k
            )

        # =========================
        # 4. GET GRAPH RELATIONSHIPS
        # =========================
        for row in results:
            chunk_id = row.get("chunk_id")

            if not chunk_id:
                row["relationships"] = []
                continue

            row["relationships"] = (
                self.graph_repository
                .get_chunk_relationships(str(chunk_id))
            )
        
        return results