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
        # 1. VECTOR RETRIEVAL (MAIN)
        # =========================
        pg_results = self.vector_repository.semantic_search(
            query=query,
            category=category,
            top_k=top_k
        )

        combined = {}
        seen = set()            

        # add PG results first (HIGH PRIORITY)
        for row in pg_results:
            cid = row.get("chunk_id") or row.get("id") or row.get("content")

            if cid in seen:
                continue

            row["source"] = "postgres"
            combined[cid] = row
            seen.add(cid)

        # =========================
        # 2. OPTIONAL RERANK
        # =========================

        if use_llm_rerank and self.rerank_service and len(pg_results) > 3:
            pg_results = self.rerank_service.rerank(
                query=query,
                results=pg_results,
                top_k=rerank_top_k
            )

        # =========================
        # 3. GRAPH EXPANSION (NEO4J)
        # =========================
        neo_results = []

        for row in pg_results:
            chunk_id = row.get("chunk_id")

            if not chunk_id:
                continue

            expanded = self.graph_repository.expand_chunk(chunk_id)
            neo_results.extend(expanded)

        for row in neo_results:
            cid = row.get("chunk_id")

            if not cid or cid in seen:
                continue

            row["source"] = "neo4j_expansion"
            combined[cid] = row
            seen.add(cid)

        # =========================
        # 3. FINAL LIST
        # =========================
        return list(combined.values())[:top_k]