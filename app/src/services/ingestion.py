from app.src.models.chunk import Chunk

class IngestionService:

    def __init__(
        self,
        pdf_service,
        chunking_service,
        hashing_service,
        version_service,
        embedding_service,
        triple_service,
        document_repo,
        chunk_repo,
        graph_repo,
        hash_repo,
        triple_repo
    ):
        self.pdf_service = pdf_service
        self.chunking_service = chunking_service
        self.hashing_service = hashing_service
        self.version_service = version_service
        self.embedding_service = embedding_service
        self.triple_service = triple_service
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.graph_repo = graph_repo
        self.hash_repo = hash_repo
        self.triple_repo = triple_repo

    def ingest(self, conn, metadata, files):
        version = self.version_service.assign_version(metadata)

        # 1. Extract + merge text
        merged_text = "\n".join(
            self.pdf_service.extract_text(f["path"])
            for f in files
        )

        # 2. Create document
        document_id = self.document_repo.insert(
            metadata=metadata,
            source=";".join(f["path"] for f in files),
        )

        # 3. Split into articles
        articles = self.chunking_service.split_articles(merged_text)

        for article in articles:
            article_no = self.chunking_service.extract_article_number(article)

            if not self.hashing_service.is_changed(
                document_code=metadata["document_code"],
                article_no=article_no,
                text=article
            ):
                continue

            # 5. Embedding
            embedding = self.embedding_service.embed_passage(article)

            chunk = Chunk(
                document_id=document_id,
                article_number=article_no,
                content=article,
                category=metadata.get("category"),
                embedding=embedding
            )

            # 6. Save chunk
            chunk_id = self.chunk_repo.insert(chunk)

            # 7. Save version/hash tracking
            self.hashing_service.save_hash_record(
                document_code=metadata["document_code"],
                article_no=article_no,
                text=article,
                version=version,
                effective_from=metadata.get("effective_from"),
                effective_to=metadata.get("effective_to"),
                chunk_id=chunk_id
            )

            # 8. Extract triples
            triples_data = self.triple_service.extract([article[:2500]])
            triples = triples_data[0].get("triples", []) if triples_data else []

            # 9. Save graph
            self.graph_repo.save_legal_chunk(
                metadata=metadata,
                chunk_id=chunk_id,
                article_no=article_no,
                content=article,
                triples=triples
            )

            conn.commit()

        print(f"✅ Hoàn thành {metadata['title']} | Version {version}")