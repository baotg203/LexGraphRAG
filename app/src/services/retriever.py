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
        rerank_top_k=5
    ):
        pg_results = (
            self.vector_repository
            .semantic_search(
                query=query,
                category=category,
                top_k=top_k * 2
            )
        )

        print(f"Postgres results: {len(pg_results)}")

        neo_results = (
            self.graph_repository
            .retrieve_latest(
                category=category,
                top_k=top_k
            )
        )

        print(f"Neo4j results: {len(neo_results)}")

        combined = []
        seen = set()

        for row in pg_results:
            content = row["content"]

            if content in seen:
                continue

            row["source"] = "postgres"

            combined.append(row)
            seen.add(content)

        for row in neo_results:
            content = row["content"]

            if content in seen:
                continue

            row["source"] = "neo4j"

            combined.append(row)
            seen.add(content)

        combined.sort(
            key=lambda x: (
                1 if x.get("effective_to") is None else 0,
                x.get("version", 0),
                x.get("similarity", 0)
            ),
            reverse=True
        )

        results = combined[:top_k]

        if (
            use_llm_rerank
            and self.rerank_service
            and len(results) > 3
        ):
            return self.rerank_service.rerank(
                query,
                results,
                rerank_top_k
            )
        print('='*50)

        return results