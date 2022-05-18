from django.urls import reverse
from arkid.config import get_app_config
from arkid.core.extension.app_protocol import AppProtocolExtension
from .appscheme import (
    Oauth2ConfigSchema, OIDCConfigSchema,
)
from oauth2_provider.models import Application
from oauth2_provider.urls import urlpatterns as urls
from arkid.core.extension import create_extension_schema

import uuid

package='com.longgui.auth.oauth2_server'

OIDCConfigSchema = create_extension_schema('OIDCConfigSchema',package, base_schema=OIDCConfigSchema)
Oauth2ConfigSchema = create_extension_schema('Oauth2ConfigSchema',package, base_schema=Oauth2ConfigSchema)
class OAuth2ServerExtension(AppProtocolExtension):

    def load(self):
        # 加载url地址
        self.load_urls()
        # 加载相应的配置文件
        self.register_app_protocol_schema(OIDCConfigSchema, 'OIDC')
        self.register_app_protocol_schema(Oauth2ConfigSchema, 'OAuth2')
        super().load()

    def load_urls(self):
        self.register_routers(urls, True)

    def create_app(self, event, **kwargs):
        config = event.data.config
        return self.update_app_data(event, config, True)

    def update_app(self, event, **kwargs):
        config = event.data.config
        return self.update_app_data(event, config, False)

    def delete_app(self, event, **kwargs):
        # 删除应用
        Application.objects.filter(name=event.data.id).delete()
        return True

    def update_app_data(self, event, config, is_create):
        '''
        修改应用程序
        '''
        app = event.data
        tenant = event.tenant
        host = get_app_config().get_frontend_host()

        client_type = config.client_type.value
        redirect_uris = config.redirect_uris
        grant_type = config.grant_type.value
        skip_authorization = config.skip_authorization
        app_type = app.app_type
        algorithm = config.algorithm.value

        obj = Application()
        if is_create is False:
            uuid_id = uuid.UUID(app.id)
            obj = Application.objects.filter(name=uuid_id).first()
        else:
            obj.name = app.id
        obj.client_type = client_type
        obj.redirect_uris = redirect_uris
        obj.skip_authorization = skip_authorization
        obj.authorization_grant_type = grant_type
        if algorithm and app_type == 'OIDC':
            obj.algorithm = algorithm
        obj.save()
        # 更新地址信息
        self.update_url_data(tenant.id, config, obj)
        return True
    
    def update_url_data(self, tenant_id, config, obj):
        '''
        更新配置中的url信息
        '''
        host = get_app_config().get_frontend_host()

        config.userinfo = host+reverse("com_longgui_auth_oauth2_server:oauth-user-info", args=[tenant_id])
        config.authorize = host+reverse("com_longgui_auth_oauth2_server:authorize", args=[tenant_id])
        config.token = host+reverse("com_longgui_auth_oauth2_server:token", args=[tenant_id])
        config.logout = host+reverse("com_longgui_auth_oauth2_server:oauth-user-logout", args=[tenant_id])
        config.client_id = obj.client_id
        config.client_secret = obj.client_secret
        config.skip_authorization = obj.skip_authorization


extension = OAuth2ServerExtension(
    package=package,
    description='OAuth2认证服务',
    version='1.0',
    labels='oauth',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)