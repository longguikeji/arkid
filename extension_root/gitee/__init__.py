import typing
from runtime import Runtime
from extension.models import Extension
from django.urls import path, include

from common.provider import ExternalIdpProvider
from .user_info_manager import GiteeUserInfoManager
from .settings import CLIENT_ID, SECRET_ID


class GiteeExternalIdpProvider(ExternalIdpProvider):

    bind_key: str = "gitee_user_id"
    name: str
    manager: GiteeUserInfoManager

    def __init__(self) -> None:
        self.manager = GiteeUserInfoManager(
            client_id=CLIENT_ID, client_secret=SECRET_ID
        )
        super().__init__()

    def bind(self, user: any, data: typing.Dict):
        from .models import GiteeUser

        GiteeUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            gitee_user_id=data.get("user_id"),
        )


class GiteeExternalIdpExtension(Extension):
    def start(self, runtime: Runtime, *args, **kwargs):
        runtime.register_external_idp(
            id="gitee",
            name="Gitee",
            description="Gitee",
            provider=GiteeExternalIdpProvider(),
        )
        super().start(runtime=runtime, *args, **kwargs)


extension = GiteeExternalIdpExtension(
    name="gitee",
    description="gitee as the external idP",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="insfocus@gmail.com",
)
