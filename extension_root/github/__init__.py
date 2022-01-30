from common.extension import InMemExtension

from .serializers import GithubExternalIdpSerializer
from .provider import GithubExternalIdpProvider
from runtime import Runtime
from .constants import KEY


class GithubExternalIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name='Github',
            description='Github',
            provider=GithubExternalIdpProvider,
            serializer=GithubExternalIdpSerializer,
        )

        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name='Github',
            description='Github',
            provider=GithubExternalIdpProvider,
            serializer=GithubExternalIdpSerializer,
        )


    def get_unbind_url(self, user):
        '''
        如果是第三方登录需要实现这个方法方便解绑
        '''
        from .models import GithubUser as User
        return self.generation_result(user, User)

extension = GithubExternalIdpExtension(
    name='github',
    tags='login',
    scope='tenant',
    type='tenant',
    description='github as the external idP',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='hanbin@jinji-inc.com',
)
