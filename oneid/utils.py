'''
basic utils
- redis-client
'''
from sys import _getframe

from django.conf import settings

from ..common.setup_utils import validate_attr
from ..common.redis_utils import RedisStorage


validate_attr(_getframe().f_code.co_filename, _getframe().f_code.co_name, _getframe().f_lineno,
              'REDIS_CONFIG')

single_redis_client = RedisStorage(    # pylint: disable=invalid-name
    host=settings.REDIS_CONFIG['HOST'],
    port=settings.REDIS_CONFIG['PORT'],
    db=settings.REDIS_CONFIG['DB'],
    password=settings.REDIS_CONFIG['PASSWORD'],
)

redis_conn = single_redis_client.redisStorage    # pylint: disable=invalid-name
