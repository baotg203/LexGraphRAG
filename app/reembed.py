from app.core.db import get_connection
from app.src.services.embedding import EmbeddingService
from app.src.repositories.chunk_repository import ChunkRepository
from app.core.embedding import EMBEDDING_MODELS
from tqdm import tqdm

DEVICE = "cuda"
BATCH_SIZE = 4


def main():
    embedding_service = EmbeddingService(
        model_id=EMBEDDING_MODELS['vi'],
        device=DEVICE,
        trust_remote_code=True
    )

    conn = get_connection()
    cur = conn.cursor()

    repo = ChunkRepository(cur)

    chunks = repo.get_all_chunks()

    print(f"Found {len(chunks)} chunks")

    for start in tqdm(range(0, len(chunks), BATCH_SIZE)):
        batch = chunks[start:start + BATCH_SIZE]

        ids = [row[0] for row in batch]
        texts = [row[1] for row in batch]

        embeddings = embedding_service.embed_passages(texts)

        for chunk_id, embedding in zip(ids, embeddings):
            repo.update_embedding(
                chunk_id=chunk_id,
                embedding=embedding
            )

        conn.commit()

    cur.close()
    conn.close()

    print("Done!")


if __name__ == "__main__":
    main()