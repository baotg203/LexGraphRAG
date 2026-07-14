from app.src.services.memory import MemoryService
from underthesea import pos_tag

FOLLOWUP_PREFIXES = {
    "còn", "vậy", "thế", "rồi", "tiếp"
}

REFERENCE_WORDS = {
    "này", "đó", "kia", "nó", "điều", "trường_hợp"
}

class RewriteService:

    def __init__(self, llm_service):
        self.llm = llm_service

    def is_followup(self, query: str, history=[]) -> bool:
        if not history:
            return False

        tokens = pos_tag(query.lower())

        words = [w for w, _ in tokens]
        tags = [t for _, t in tokens]

        # 1. Bắt đầu bằng từ nối
        if words and words[0] in FOLLOWUP_PREFIXES:
            return True

        # 2. Có đại từ tham chiếu
        if any(w in REFERENCE_WORDS for w in words):
            return True

        # 3. Không có động từ và câu rất ngắn
        if len(tokens) <= 4 and "V" not in tags:
            return True

        return False

    def rewrite(self, query: str, history: list) -> str:
        """
        Rewrite follow-up question thành standalone question.
        """

        if not history:
            return query

        history_text = ""

        for message in history[-6:]:     # lấy 3 lượt hội thoại = 6 messages
            role = message["role"].capitalize()
            content = message["content"]
            history_text += f"{role}: {content}\n"

        prompt = f"""
Bạn là hệ thống rewrite truy vấn pháp luật.

Nhiệm vụ:

Viết lại câu hỏi cuối cùng thành câu hỏi độc lập.

QUY TẮC

1. Không được trả lời.
2. Không được giải thích.
3. Không được suy luận ngoài hội thoại.
4. Chỉ bổ sung chủ ngữ hoặc đối tượng còn thiếu.
5. Giữ nguyên thuật ngữ pháp luật.
6. Nếu câu hỏi đã đầy đủ thì giữ nguyên.



Lịch sử hội thoại:

{history_text}

Câu hỏi hiện tại:

{query}

LƯU Ý QUAN TRỌNG: Nếu câu hỏi không đúng chủ đề thì trả về  "Câu hỏi không liên quan đến chủ đề pháp luật."

Standalone question:
"""

        rewritten = self.llm.generate(prompt).strip()

        return rewritten if rewritten else query