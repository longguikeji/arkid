from common.extension import InMemExtension
from .serializers import GiteeExternalIdpSerializer
from .provider import GiteeExternalIdpProvider
from runtime import Runtime
from .constants import KEY


class GiteeExternalIdpExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            key=KEY,
            name="Gitee",
            description="Gitee External idP",
            provider=GiteeExternalIdpProvider,
            serializer=GiteeExternalIdpSerializer,
        )
        super().start(runtime=runtime, *args, **kwargs)
    
    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_external_idp(
            key=KEY,
            name="Gitee",
            description="Gitee External idP",
            provider=GiteeExternalIdpProvider,
            serializer=GiteeExternalIdpSerializer,
        )

    def get_unbind_url(self, user):
        '''
        如果是第三方登录需要实现这个方法方便解绑
        '''
        from .models import GiteeUser as User
        return self.generation_result(user, User)



extension = GiteeExternalIdpExtension(
    name="gitee",
    tags='login',
    scope='tenant',
    type='tenant',
    description="gitee as the external idP",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="hanbin@jinji-inc.com",
)
