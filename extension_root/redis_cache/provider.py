import typing
from common.provider import CacheProvider
import redis


class RedisCacheProvider(CacheProvider):

    def __init__(self, host, port, password, db: int=0) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.db = db

    def set(self, key: str, value: any, expired: typing.Optional[int]=None):
        conn = redis.StrictRedis(
            host=self.host, 
            port=self.port, 
            password=self.password,
            db=self.db,
            decode_responses=True
        )
        conn.set(key, value, ex=expired)

    def get(self, key: str) -> any:
        conn = redis.StrictRedis(
            host=self.host, 
            port=self.port, 
            password=self.password,
            db=self.db
        )
        return conn.get(key)

    def __getattr__(self, key):
        conn = redis.StrictRedis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db
        )
        return getattr(conn, key)
