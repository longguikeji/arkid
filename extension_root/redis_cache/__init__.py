from .extension import RedisCacheExtension


extension = RedisCacheExtension(
    scope='global',
    type='global',
    name='redis_cache',
    tags='cache',
    description='Redis based cache provider',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='hanbin@jinji-inc.com',
)
