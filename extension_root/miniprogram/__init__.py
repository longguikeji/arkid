from common.extension import InMemExtension
from .constants import KEY
from runtime import Runtime
from .provider import MiniProgramExternalIdpProvider
from .serializers import MiniProgramExternalIdpSerializer


class MiniProgramExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name='微信小程序',
            description='一种不需要下载安装即可使用的应用，它实现了应用“触手可及”的梦想',
            provider=MiniProgramExternalIdpProvider,
            serializer=MiniProgramExternalIdpSerializer,
        )
        super().start(runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name='微信小程序',
            description='一种不需要下载安装即可使用的应用，它实现了应用“触手可及”的梦想',
            provider=MiniProgramExternalIdpProvider,
            serializer=MiniProgramExternalIdpSerializer,
        )

    def get_unbind_url(self, user):
        '''
        如果是第三方登录需要实现这个方法方便解绑
        '''
        from .models import MiniProgramUser as User
        return self.generation_result(user, User)


extension = MiniProgramExtension(
    name='miniprogram',
    tags='login',
    scope='tenant',
    type='tenant',
    description='微信小程序',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='hanbin@jinji-inc.com',
)
