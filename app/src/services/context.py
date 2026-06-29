class ContextService:
    def __init__(self):
        pass

    def build_context(self, results: list[dict]) -> str:
        if not results:
            return ""

        contexts = []

        for i, chunk in enumerate(results, start=1):
            version = f"Version {chunk.get('version', 'N/A')}"

            effective_from = chunk.get("effective_from")
            if effective_from:
                version += f" ({effective_from})"

            if chunk.get("effective_to") is None:
                version += " - Hiệu lực hiện hành"

            contexts.append(
                f"""
                ĐIỀU {i} - {version}
                Tiêu đề: {chunk.get('title', '')}
                Nguồn: {chunk.get('source', 'postgres').upper()}

                {chunk.get('content', '')}
                {'-' * 80}
                """.strip()
            )

        return "\n\n".join(contexts)