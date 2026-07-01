import json
import logging
import re
from typing import Any, Union, List, Dict
from json_repair import repair_json

logger = logging.getLogger(__name__)


class TripleService:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    def extract(self, articles: list[str]) -> list:
        """Extract triples from articles using LLM."""
        prompt = self._build_prompt(articles)

        try:
            raw_output = self.llm_service.generate(prompt)
            logger.debug(f"Raw LLM output (first 400 chars): {raw_output[:400]}...")

            parsed = self._clean_json(raw_output)

            # Normalize to list of {"index": i, "triples": [...]}
            normalized = []

            if isinstance(parsed, list):
                for i, item in enumerate(parsed):
                    if isinstance(item, dict) and "triples" in item:
                        triples = item["triples"]
                    elif isinstance(item, list):
                        triples = item
                    else:
                        triples = [item] if isinstance(item, dict) else []

                    normalized.append({
                        "index": i,
                        "triples": triples
                    })
                return normalized

            elif isinstance(parsed, dict):
                triples = parsed.get("triples", [parsed])
                return [{"index": 0, "triples": triples}]

            return []

        except Exception as e:
            logger.exception("Triple extraction failed")
            return []

    def _build_prompt(self, articles: list[str]) -> str:
        return f"""
Bạn là chuyên gia luật Việt Nam.

Hãy trích xuất các bộ ba (subject-predicate-object) cho từng điều luật.

**Trả về đúng định dạng JSON sau (không thêm text nào khác):**

[
  {{"triples": [{{"subject": "", "predicate": "", "object": ""}}]}},
  {{"triples": [...]}}
]

TEXT:
{json.dumps(articles, ensure_ascii=False)}
"""

    @staticmethod
    def _clean_json(text: str) -> Union[Dict, List, Any]:
        if not text or not isinstance(text, str):
            raise ValueError("Input phải là string không rỗng")

        original_text = text
        text = text.strip()

        # Pre-cleaning mạnh (giúp repair_json chạy nhanh hơn)
        text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\uFEFF]', '', text)  # control chars
        text = re.sub(r'\s+', ' ', text)  # normalize whitespace

        # 1. Thử parse chuẩn trước (nhanh nhất)
        try:
            parsed = json.loads(text)
            logger.info("✅ JSON parsed directly")
            return parsed
        except json.JSONDecodeError:
            pass

        # 2. Dùng repair_json (với optimize)
        try:
            parsed = repair_json(
                text, 
                return_objects=True,      # Quan trọng: nhanh hơn
                skip_json_loads=True      # Vì đã thử json.loads ở trên
            )
            logger.info("✅ JSON repaired successfully")
            return parsed
        except Exception as e:
            logger.warning(f"repair_json failed: {str(e)[:150]}")

        # 3. Aggressive fallback
        try:
            cleaned = text
            cleaned = re.sub(r'-\s*', '', cleaned)                    # stray dashes
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)         # trailing comma
            cleaned = re.sub(r'(\b\w+\b)\s*:', r'"\1":', cleaned)    # unquoted keys (cẩn thận)
            cleaned = re.sub(r':\s*(\w+)(?=[,}])', r': "\1"', cleaned)  # unquoted values

            parsed = json.loads(cleaned)
            logger.info("✅ JSON parsed with aggressive cleaning")
            return parsed
        except Exception as e2:
            raise ValueError(
                f"Không parse được JSON sau tất cả các cách.\n"
                f"Error: {e2}\n"
                f"First 800 ký tự:\n{original_text[:800]}..."
            ) from e2