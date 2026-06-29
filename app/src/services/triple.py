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
        try:
            parsed = repair_json(text)
            logger.info("✅ JSON parsed successfully")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}")
            try:
                # One more aggressive attempt
                cleaned = re.sub(r'-\s*', '', text)   # remove any remaining dashes
                parsed = json.loads(cleaned)
                return parsed
            except json.JSONDecodeError:
                raise ValueError(
                    f"JSON parse failed after all fixes.\n"
                    f"Error: {e}\n"
                    f"First 800 chars:\n{text[:800]}..."
                ) from e