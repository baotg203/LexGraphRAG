from config import THRESHOLD_SIMILARITY


class ChatService:
    def __init__(
        self,
        retriever_service,
        context_service,
        llm_service
    ):
        self.retriever_service = retriever_service
        self.context_service = context_service
        self.llm_service = llm_service

    def ask(self, question: str):
        results = self.retriever_service.retrieve(
            query=question,
            use_llm_rerank=True
        )

        if not results:
            return {
                "answer":
                    "Nội dung câu hỏi hiện chưa đủ cơ sở pháp lý để đối chiếu với các quy định hiện hành. Vui lòng liên hệ chuyên gia để được tư vấn cụ thể hơn.",
                "citations": []
            }

        best_chunk = results[0]

        if best_chunk.get("similarity", 0) < THRESHOLD_SIMILARITY:
            return {
                "answer":
                    "Nội dung câu hỏi hiện chưa đủ cơ sở pháp lý để đối chiếu với các quy định hiện hành. Vui lòng liên hệ chuyên gia để được tư vấn cụ thể hơn.",
                "citations": []
            }

        context = self.context_service.build_context(results)

        answer = self.llm_service.answer(
            question=question,
            context=context
        )

        citations = [
            {
                "chunk_id": chunk.get("chunk_id"),
                "article_number": chunk.get("article_number"),
                "version": chunk.get("version"),
                "title": chunk.get("title"),
                "content": (
                    chunk.get("content", "")[:800] + "..."
                    if len(chunk.get("content", "")) > 800
                    else chunk.get("content")
                ),
                "effective_from": chunk.get("effective_from")
            }
            for chunk in results[:3]
        ]

        return {
            "answer": answer,
            "citations": citations,
            "used_version": best_chunk.get("version"),
            "source_count": len(results)
        }