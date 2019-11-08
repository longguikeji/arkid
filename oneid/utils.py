'''
basic utils
- redis-client
'''
from django.conf import settings

from common.redis_utils import RedisStorage

single_redis_client = RedisStorage(    # pylint: disable=invalid-name
    host=settings.REDIS_CONFIG['HOST'],
    port=settings.REDIS_CONFIG['PORT'],
    db=settings.REDIS_CONFIG['DB'],
    password=settings.REDIS_CONFIG['PASSWORD'],
)

redis_conn = single_redis_client.redisStorage    # pylint: disable=invalid-name
