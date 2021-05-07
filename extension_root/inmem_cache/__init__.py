from .extension import InMemCacheExtension


extension = InMemCacheExtension(
    scope='global',
    type='global',
    name='inmem_cache',
    tags='cache',
    description='In Memery cache provider',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='support@longguikeji.com',
)
