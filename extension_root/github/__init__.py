import typing
from runtime import Runtime
from extension.models import Extension
from django.urls import path, include

from common.provider import ExternalIdpProvider
from .user_info_manager import GithubUserInfoManager
from .settings import CLIENT_ID, SECRET_ID


class GithubExternalIdpProvider(ExternalIdpProvider):

    bind_key: str = 'github_user_id'
    name: str
    manager: GithubUserInfoManager

    def __init__(self) -> None:
        self.manager = GithubUserInfoManager(client_id=CLIENT_ID, client_secret=SECRET_ID)
        super().__init__()

    def bind(self, user: any, data: typing.Dict):
        from .models import GithubUser
        GithubUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            github_user_id=data.get('user_id'),
        )

class GithubExternalIdpExtension(Extension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            id='github', 
            name='Github', 
            description='Github',
            provider=GithubExternalIdpProvider(),
        )
        super().start(runtime=runtime, *args, **kwargs)


extension = GithubExternalIdpExtension(
    name='github',
    description='github as the external idP',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
