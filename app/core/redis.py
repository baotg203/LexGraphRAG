import redis

from config import REDIS_CONFIG


class RedisClient:

    _instances = {}


    @classmethod
    def get_client(
        cls,
        decode_responses=True
    ):

        key = decode_responses

        if key not in cls._instances:

            cls._instances[key] = redis.Redis(

                host=REDIS_CONFIG['host'],

                port=REDIS_CONFIG['port'],

                db=REDIS_CONFIG['db'],

                password=REDIS_CONFIG['password'],

                decode_responses=decode_responses,

                health_check_interval=30
            )

        return cls._instances[key]