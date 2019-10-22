# coding:utf-8
from functools import wraps
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
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=True, password=password)
        self.redisStorage = redis.StrictRedis(connection_pool=self.pool, db=db)

redisStorage = RedisStorage().redisStorage
