class ContextService:
    def __init__(self):
        pass

    def format_history(self, history, max_turns=3):
        if not history:
            return "Không có."

        history = history[-max_turns * 2:]

        lines = []

        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")

        return "\n".join(lines)

    def build_context(self, results: list[dict], history) -> str:
        if not results:
            return ""

        contexts = []
        contexts.append(
            f"""
            [Lịch sử hội thoại]
            {self.format_history(history)}
            """.strip()
        )

        for i, chunk in enumerate(results, start=1):
            version = f"Version {chunk.get('version', 'N/A')}"

            effective_from = chunk.get("effective_from")
            if effective_from:
                version += f" ({effective_from})"

            if chunk.get("effective_to") is None:
                version += " - Hiệu lực hiện hành"

            # =========================
            # Relationships
            # =========================
            relationship_text = ""

            relationships = chunk.get("relationships", [])

            if relationships:
                lines = []

                for rel in relationships:
                    subject = rel.get("subject", "")
                    predicate = rel.get("predicate", "")
                    obj = rel.get("object", "")

                    if subject or predicate or obj:
                        lines.append(
                            f"- {subject} → {predicate} → {obj}"
                        )

                if lines:
                    relationship_text = (
                        "\nQuan hệ pháp lý liên quan:\n"
                        + "\n".join(lines)
                    )

            contexts.append(
                f"""
    [Tài liệu {i}]
    Tiêu đề: {chunk.get('title', '')}
    Phiên bản: {version}

    Nội dung:
    {chunk.get('content', '')}
    {relationship_text}

    {'-' * 80}
                """.strip()
            )

        return "\n\n".join(contexts)