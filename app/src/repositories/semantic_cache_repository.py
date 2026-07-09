import json
import time
import uuid
import redis
import numpy as np

from redis.commands.search.field import (
    TextField,
    NumericField,
    VectorField
)

from redis.commands.search.index_definition import IndexDefinition, IndexType

from redis.commands.search.query import Query


class SemanticCacheRepository:

    INDEX_NAME = "semantic_cache_idx"
    PREFIX = "semantic_cache:"

    VECTOR_DIM = 768


    def __init__(
        self,
        redis_client: redis.Redis
    ):
        self.redis = redis_client

        self._create_index()


    def _create_index(self):

        try:
            self.redis.ft(
                self.INDEX_NAME
            ).info()

            return

        except Exception:
            pass


        schema = (

            TextField(
                "context_signature",
            ),

            TextField(
                "answer",
            ),

            TextField(
                "chunk_ids",
            ),

            NumericField(
                "created_at",
            ),

            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.VECTOR_DIM,
                    "DISTANCE_METRIC": "COSINE",
                    "M": 16,
                    "EF_CONSTRUCTION": 200
                }
            )
        )


        definition = IndexDefinition(
            prefix=[
                self.PREFIX
            ],
            index_type=IndexType.HASH
        )


        self.redis.ft(
            self.INDEX_NAME
        ).create_index(
            fields=schema,
            definition=definition
        )


    def save(
        self,
        embedding,
        context_signature,
        answer,
        chunk_ids,
        ttl=604800
    ):

        cache_id = str(uuid.uuid4())

        key = (
            self.PREFIX
            +
            cache_id
        )

        data = {

            "embedding": np.array(
                embedding,
                dtype=np.float32
            ).tobytes(),

            "context_signature": context_signature,

            "answer": answer,

            "chunk_ids": json.dumps(chunk_ids),

            "created_at": time.time()
        }

        self.redis.hset(
            key,
            mapping=data
        )


        self.redis.expire(
            key,
            ttl
        )


        return cache_id



    def search(
        self,
        embedding,
        limit=5
    ):

        vector = np.array(
            embedding,
            dtype=np.float32
        ).tobytes()


        query = (
            Query(
                f"""
                *=>[KNN {limit} @embedding $vec AS score]
                """
            )
            .sort_by(
                "score"
            )
            .return_fields(
                "context_signature",
                "answer",
                "chunk_ids",
                "score"
            )
            .dialect(2)
        )


        params = {
            "vec": vector
        }


        result = (
            self.redis.ft(
                self.INDEX_NAME
            )
            .search(
                query,
                query_params=params
            )
        )

        return [
            {
                "context_signature": doc.context_signature,

                "answer": doc.answer,

                "chunk_ids": json.loads(
                    doc.chunk_ids
                ),

                "score": float(
                    doc.score
                )
            }
            for doc in result.docs
        ]