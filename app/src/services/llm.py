import requests

from config import OLLAMA_CONFIG


class LLMService:
    def __init__(self):
        self.base_url = (
            f"{OLLAMA_CONFIG['uri']}:"
            f"{OLLAMA_CONFIG['port']}"
        )

        self.model = OLLAMA_CONFIG["model"]

    def generate(
        self,
        prompt: str,
        stream: bool = False
    ) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream
                },
                timeout=300
            )

            response.raise_for_status()

            return response.json()["response"]

        except requests.RequestException as e:
            raise RuntimeError(
                f"Ollama error: {e}"
            )
        
    def answer(self, 
               question: str, 
               context: str) -> str:
        if not context.strip():
            return "Không tìm thấy căn cứ trong văn bản luật."

        prompt = f"""
    Bạn là luật sư tư vấn pháp luật hôn nhân và gia đình Việt Nam.

    QUY TẮC BẮT BUỘC:
    - CHỈ sử dụng thông tin trong CONTEXT
    - TUYỆT ĐỐI KHÔNG hiển thị CHUNK_ID, số hiệu chunk, hay mã kỹ thuật
    - TUYỆT ĐỐI KHÔNG viết "CHUNK xxx" trong câu trả lời

    NGÔN NGỮ BẮT BUỘC:
    - Toàn bộ câu trả lời PHẢI bằng tiếng Việt.
    - Sau khi sinh câu trả lời, PHẢI tự kiểm tra.
    - Nếu phát hiện bất kỳ từ, ký tự, câu nào không phải tiếng Việt
    → PHẢI viết lại đoạn đó bằng tiếng Việt trước khi trả lời.


    CÁCH TRẢ LỜI:

    <tối đa 3–4 câu, dễ hiểu, nếu gặp câu trả lời dài thì hãy trả lời dạng liệt kê>


    ---
    CONTEXT:
    {context}
    ---

    Câu hỏi: {question}
    """

        return self.generate(prompt).strip()