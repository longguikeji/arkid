"""
SAML 2.0  插件处理
"""
from common.extension import InMemExtension
from .providers.idp import Saml2IdpProvider,Saml2IdpFileProvider,Saml2IdpAliyunRoleProvider
from runtime import Runtime
from .constants import KEY
from .serializers.idp import SAML2IdpBaseSerializer,Saml2IdpFileSerializer,Saml2IdpAliyunRoleSerializer


class SAML2Extension(InMemExtension):
    """
    SAML2 插件
    """

    def start(self, runtime: Runtime, *args, **kwargs):
        
        
        runtime.register_authorization_server(
            id='saml2idp',
            name='SAML2.0 IDP',
            description='SAML2.0 IDP',
        )
        runtime.register_app_type(
            key='saml2_idp',
            name='SAML2 IDP',
            provider=Saml2IdpProvider,
            serializer=SAML2IdpBaseSerializer
        )
        runtime.register_app_type(
            key='saml2_idp_file',
            name='SAML2 IDP metadata文件配置',
            provider=Saml2IdpFileProvider,
            serializer=Saml2IdpFileSerializer
        )
        runtime.register_app_type(
            key='saml2_idp_aliyun_role',
            name='SAML2 IDP 阿里云角色SSO',
            provider=Saml2IdpAliyunRoleProvider,
            serializer=Saml2IdpAliyunRoleSerializer
        )
        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):
        runtime.logout_authorization_server(
            id='saml2idp',
            name='SAML2.0 IDP',
            description='SAML2.0 IDP',
        )
        runtime.logout_app_type(
            key='saml2idp',
            name='SAML2 IDP',
            provider=Saml2IdpProvider,
            serializer=SAML2IdpBaseSerializer
        )
        runtime.logout_app_type(
            key='saml2_idp_file',
            name='SAML2 IDP metadata文件配置',
            provider=Saml2IdpFileProvider,
            serializer=Saml2IdpFileSerializer
        )
        runtime.logout_app_type(
            key='saml2_idp_aliyun_role',
            name='SAML2 IDP 阿里云角色SSO',
            provider=Saml2IdpAliyunRoleProvider,
            serializer=Saml2IdpAliyunRoleSerializer
        )

extension = SAML2Extension(
    tags='saml',
    name=KEY,
    scope='tenant',
    type='tenant',
    description="SAML2 Protocol",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="guancyxx@guancyxx.cn",
)
