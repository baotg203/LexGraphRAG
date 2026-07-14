from config import THRESHOLD_SIMILARITY


class ChatService:
    def __init__(
        self,
        retriever_service,
        context_service,
        llm_service,
        memory_service,
        semantic_cache_service,
        context_signature,
        rewrite_service
    ):
        self.retriever_service = retriever_service
        self.context_service = context_service
        self.llm_service = llm_service
        self.memory_service = memory_service
        self.semantic_cache_service = semantic_cache_service
        self.context_signature = context_signature
        self.rewrite_service = rewrite_service

    def ask(self, question: str, session_id):
        results = self.retriever_service.retrieve(
            query=question,
            use_llm_rerank=True
        )

        history = self.memory_service.get_history(session_id)

        if not results or results[0].get("similarity", 0) < THRESHOLD_SIMILARITY:

            rewrite_question = None

            is_followup = self.rewrite_service.is_followup(
                query=question,
                history=history
            )
            
            if history and is_followup:
                rewrite_question = self.rewrite_service.rewrite(
                    query=question,
                    history=history
                )
                question = rewrite_question
            
            if not rewrite_question or rewrite_question == "Câu hỏi không liên quan đến chủ đề pháp luật.":
                return {
                    "answer":
                        "Nội dung câu hỏi hiện chưa đủ cơ sở pháp lý để đối chiếu với các quy định hiện hành. Vui lòng liên hệ chuyên gia để được tư vấn cụ thể hơn.",
                    "citations": []
                }
            

        context_signature = (
            self.context_signature
            .build(results[:3])
        )

        cached = (
            self.semantic_cache_service
            .get(
                question,
                context_signature
            )
        )

        if cached:

            return {
                "answer": cached.get("answer"),
                "citations": cached.get("citations"),
                "used_version": cached.get("used_version"),
                "source_count": cached.get("source_count"),
                "cached": True
            }

        context = self.context_service.build_context(
            results=results,
            history=history
        )

        answer = self.llm_service.answer(
            question=question,
            context=context
        )

        self.semantic_cache_service.save(
            question,
            context_signature,
            answer,
            [
                x["chunk_id"]
                for x in results[:3]
            ]
        )

        self.memory_service.append(
            session_id,
            "user",
            question
        )

        self.memory_service.append(
            session_id,
            "assistant",
            answer
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
            "used_version": results[0].get("version"),
            "source_count": len(results),
            "cached": False
        }