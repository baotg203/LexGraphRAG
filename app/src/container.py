from app.src.repositories.document_repository import DocumentRepository
from app.src.repositories.chunk_repository import ChunkRepository
from app.src.repositories.hash_repository import HashRepository
from app.src.repositories.triple_repository import TripleRepository
from app.src.repositories.graph_repository import GraphRepository
from app.src.repositories.vector_repository import VectorRepository
from app.src.repositories.chunk_repository import ChunkRepository


from app.src.services.triple import TripleService
from app.src.services.pdf_service import PdfService
from app.src.services.chunking import ChunkingService
from app.src.services.embedding import EmbeddingService
from app.src.services.llm import LLMService
from app.src.services.hashing import HashingService
from app.src.services.document_version import DocumentVersionService
from app.src.services.ingestion import IngestionService
from app.src.services.chat import ChatService
from app.src.services.retriever import RetrieverService
from app.src.services.tts import TTSService
from app.src.services.rerank import RerankService
from app.src.services.context import ContextService

from config import DEVICE
from app.core.embedding import EMBEDDING_MODELS

class IngestionContainer:
    def __init__(
        self,
        cur,
        neo4j_driver
    ):
        self.document_repo = (
            DocumentRepository(cur)
        )

        self.chunk_repo = (
            ChunkRepository(cur)
        )

        self.hash_repo = (
            HashRepository(cur)
        )

        self.graph_repo = (
            GraphRepository(
                neo4j_driver
            )
        )

        self.pdf_service = (
            PdfService()
        )

        self.chunking_service = (
            ChunkingService()
        )

        self.embedding_service = EmbeddingService(
            model_id=EMBEDDING_MODELS['vi'],
            device=DEVICE
        )

        self.triple_repo = (
            TripleRepository(cur)
        )

        self.llm_service = (
            LLMService()
        )

        self.triple_service = (
            TripleService(
                self.llm_service
            )
        )

        self.version_service = (
            DocumentVersionService(
                self.document_repo
            )
        )

        self.hashing_service = (
            HashingService(
                self.hash_repo
            )
        )

        self.ingestion_service = (
            IngestionService(
                pdf_service=self.pdf_service,
                chunking_service=self.chunking_service,
                embedding_service=self.embedding_service,
                hashing_service=self.hashing_service,
                triple_service=self.triple_service,
                graph_repo=self.graph_repo,
                version_service=self.version_service,
                document_repo=self.document_repo,
                chunk_repo=self.chunk_repo,
                hash_repo=self.hash_repo,
                triple_repo=self.triple_repo
            )
        )

class QAContainer:
    def __init__(self, db, neo4j_driver):
        self.db = db
        self.neo4j_driver = neo4j_driver        
        # =====================
        # Repositories
        # =====================

        self.embedding_service = EmbeddingService(
            model_id=EMBEDDING_MODELS['vi'],
            device=DEVICE
        )

        self.vector_repository = VectorRepository(
            db=self.db,
            embedding_model=self.embedding_service
        )

        self.graph_repository = GraphRepository(
            self.neo4j_driver
        )

        self.chunk_repository = ChunkRepository(
            cur=self.db
        )

        # =====================
        # Services
        # =====================
        self.llm_service = LLMService()

        self.rerank_service = RerankService(
            self.llm_service
        )

        self.retriever_service = RetrieverService(
            vector_repository=self.vector_repository,
            graph_repository=self.graph_repository,
            rerank_service=self.rerank_service
        )

        self.context_service = ContextService()

        self.chat_service = ChatService(
            retriever_service=self.retriever_service,
            context_service=self.context_service,
            llm_service=self.llm_service
        )

        self.tts_service = TTSService()

    def close(self):
        self.neo4j_driver.close()