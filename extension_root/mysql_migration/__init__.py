from rest_framework.serializers import Serializer
from runtime import Runtime
from common.extension import InMemExtension
from .provider import MysqlMigrationProvider
from .serializers import MysqlMigrationSerializer
from .constants import KEY


class MysqlMigrationExtension(InMemExtension):
    def start(self, runtime: Runtime, *args, **kwargs):

        from extension.models import Extension

        o = Extension.active_objects.filter(
            type=KEY,
        ).first()

        assert o is not None
        host = o.data.get('host')
        port = o.data.get('port')
        user = o.data.get('user')
        passwd = o.data.get('passwd')
        db = o.data.get('db')

        provider = MysqlMigrationProvider(host, port, user, passwd, db)
        runtime.register_migration_provider(
            provider=provider,
        )

        super().start(runtime=runtime, *args, **kwargs)


extension = MysqlMigrationExtension(
    name='mysql_migration',
    description='Migrate arkid-v1 database to arkid-v2 database',
    version='1.0',
    logo='',
    tags='mysql',
    type='global',
    scope='global',
    maintainer='北京龙归科技有限公司',
    homepage='https://www.longguikeji.com',
    contact='rock@longguikeji.com',
    serializer=MysqlMigrationSerializer,
)
