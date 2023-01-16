from typing import Union, Optional

from django.conf import settings
import redis


class RedisService:
    """
    Abstraction layer over Redis to reduce boilerplate in other services
    """

    _instance: redis.StrictRedis

    def __init__(self, *, db: int):
        self._instance = redis.StrictRedis(
            host=settings.REDIS_CONFIG.get('HOST', 'localhost'),
            port=settings.REDIS_CONFIG.get('PORT', '6379'),
            db=db,
            decode_responses=True,
        )

    def store(
        self,
        *,
        key: str,
        value: Union[bytes, str, int, float],
        expiration_seconds: Optional[int] = None
    ):
        return self._instance.set(key, value, ex=expiration_seconds)

    def retrieve(self, *, key: str):
        return self._instance.get(key)

    def retrieve_all(self):
        all_keys = self._instance.keys("*")
        return [self._instance.get(key) for key in all_keys]

    def delete(self, *, key: str):
        return self._instance.delete(key)
