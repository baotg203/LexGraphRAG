class DocumentVersionService:
    def __init__(self, document_repo):
        self.document_repo = document_repo

    def assign_version(
        self,
        metadata
    ):
        version = (
            self.document_repo
            .get_next_version(
                metadata["document_code"]
            )
        )

        metadata["version"] = version

        return version