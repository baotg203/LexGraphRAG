from app.retriever import build_context
import requests
from config import OLLAMA_CONFIG

def local_llm(prompt):
    res = requests.post(
        f"{OLLAMA_CONFIG['uri']}:{OLLAMA_CONFIG['port']}/api/generate",
        json={
            "model": OLLAMA_CONFIG['model'],
            "prompt": prompt,
            "stream": False
        }
    )
    return res.json()["response"]

def answer(question, context_text):
    if not context_text.strip():
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
{context_text}
---

Câu hỏi: {question}
"""

    return local_llm(prompt).strip()
