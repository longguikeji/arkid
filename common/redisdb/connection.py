# coding: utf-8

import redis
from ...common.decorator_utils import singleton

REDIS_DEFAULT_CONFIG = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}


class RedisFactory(object):
    def __init__(self):
        self._conn_cache = {}

    @staticmethod
    @singleton
    def get_instance():
        return RedisFactory()

    def _get_cache_key(self, host, port, db):
        return "%s:%s:%s" % (host, port, db)

    def get_conn(self, config=None, reuse=True, **kwargs):
        if not config:
            config = REDIS_DEFAULT_CONFIG

        host = config.get('HOST', 'localhost')
        port = config.get('PORT', 6379)
        db = config.get('DB', 0)
        password = config.get('PASSWORD', None)

        conn_kwargs = {
            'host': host,
            'port': port,
            'db': db,
            'password': password,
            'reuse': reuse,
        }

        socket_timeout = kwargs.get('socket_timeout', None)
        if socket_timeout:
            conn_kwargs['socket_timeout'] = socket_timeout

        return self._get_conn(**conn_kwargs)

    def _get_conn(self, host='localhost', port=6379, db=0, password=None, reuse=True, socket_timeout=None):
        kwargs = {
            'host': host,
            'port': port,
            'db': db,
            'password': password,
            'socket_timeout': socket_timeout,
        }
        if not reuse:
            return redis.Redis(**kwargs)

        cache_key = self._get_cache_key(host, port, db)
        conn = self._conn_cache.get(cache_key)
        if not conn:
            conn = redis.Redis(**kwargs)
            self._conn_cache[cache_key] = conn

        return conn


def get_conn(config=None, reuse=True, socket_timeout=None):
    """
    Get a real redis connection.

    :param dict config: a dict to describe the config of redis, default to None.
                        The template is:
                        ``{'HOST': 'localhost', 'PORT': 6379, 'DB': 0, 'PASSWORD': None}``.
                        If it's None, then will use the default configuration, which means:
                        HOST is localhost, PORT is 6379, DB is 0, PASSWORD is None.
    :param bool reuse:  return the same connection created before for the same configuration.
    :param int|None socket_timeout: set the timeout of the socket in seconds
                                    The real timeout could be twice of your setting, since
                                    it's determined by the implementation of the py redis.
                                    https://github.com/andymccurdy/redis-py/blob/2.7.6/redis/client.py#L371
    :returns: redis connection to operate on
    :rtype: redis.client.Redis
    """
    return RedisFactory().get_instance().get_conn(config, reuse, socket_timeout=socket_timeout)


def get_conn_str(config=None):
    """
    Build a redis connection str

    .. seealso:: get_conn

    :param dict config: redis configuration
    :returns: redis connection str
    :rtype: str
    """
    if config is None:
        config = REDIS_DEFAULT_CONFIG

    connstr = 'redis://{0}:{1}?db={2}'.format(config.get('HOST', 'localhost'),
                                              config.get('PORT', 6379),
                                              config.get('DB', 0))
    if config.get('PASSWORD', None):
        connstr += '&password={0}'.format(config.get('PASSWORD'))

    return connstr
