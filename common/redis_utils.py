# coding:utf-8
from functools import wraps
from settings import REDIS_HOST, REDIS_PORT, REDIS_DB
import redis


def singleton(cls):
    """
    单例装饰器
    :param cls: 类实例
    :return: 类唯一的实例
    """
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return getinstance


@singleton
class RedisStorage(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=True)
        self.redisStorage = redis.StrictRedis(connection_pool=self.pool, db=db)


redisStorage = RedisStorage().redisStorage


@singleton
class AccessTokenRedisStorage(object):
    def __init__(self):
        self.storage = redisStorage

    def get_access_token(self, app_id):
        """返回access_token
        """

        return self.storage.get('app_id_{}_access_token'.format(app_id))

    def set_access_token(self, app_id, value):
        """设置access_token
        """

        self.storage.set('app_id_{}_access_token'.format(app_id), value)

    def get_expired(self, app_id):
        """返回过期时间
        """

        return self.storage.get('app_id_{}_expired'.format(app_id))

    def set_expired(self, app_id, value):
        """设置过期时间
        """

        self.storage.set('app_id_{}_expired'.format(app_id), value)


access_token_redis_storage = AccessTokenRedisStorage()
