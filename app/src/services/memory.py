import json

from config import REDIS_CONFIG
from app.core.redis import RedisClient


class MemoryService:

    PREFIX = "chat:session"

    def __init__(self):

        self.redis = RedisClient.get_client()

    def _key(self, session_id):

        return f"{self.PREFIX}:{session_id}"

    def get_history(self, session_id):

        data = self.redis.lrange(
            self._key(session_id),
            0,
            -1
        )

        self.redis.expire(
            self._key(session_id),
            REDIS_CONFIG['session_ttl']
        )

        return [
            json.loads(x)
            for x in data
        ]

    def append(self, session_id, role, content):

        key = self._key(session_id)

        self.redis.rpush(
            key,
            json.dumps({
                "role": role,
                "content": content
            })
        )

        self.redis.ltrim(
            key,
            -REDIS_CONFIG['max_connections'],
            -1
        )

        self.redis.expire(
            key,
            REDIS_CONFIG['session_ttl']
        )

    def clear(self, session_id):

        self.redis.delete(self._key(session_id))