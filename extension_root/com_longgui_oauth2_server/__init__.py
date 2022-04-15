from arkid.core import extension
from .appscheme import (
    OIDCAppSchema, OAuth2AppSchema
)
from oauth2_provider.models import Application
from arkid.config import get_app_config

class OAuth2ServerExtension(extension.Extension):

    def load(self):
        super().load()
        # 加载url地址
        self.load_urls()
        # 加载相应的配置文件
        # self.register_config_schema(OIDCAppSchema, self.package)
        # self.register_config_schema(OAuth2AppSchema, self.package)


    def load_urls(self):
        from django.urls import include, re_path

        urls = [
            re_path(r'^o/', include('oauth2_provider.urls'))
        ]

        self.register_routers(urls, True)
    
    def create(self, tenant, app, data):
        client_type = data.get('client_type')
        skip_authorization = data.get('skip_authorization')
        redirect_uris = data.get('redirect_uris')
        authorization_grant_type = data.get('grant_type')
        algorithm = data.get('algorithm')
        host = get_app_config().get_frontend_host()

        obj = Application()
        obj.name = app.id
        obj.client_type = client_type
        obj.skip_authorization = skip_authorization
        obj.redirect_uris = redirect_uris
        if algorithm and app.type == 'OIDC':
            obj.algorithm = algorithm
        obj.authorization_grant_type = authorization_grant_type
        obj.save()

        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'skip_authorization': obj.skip_authorization,
            'userinfo': host+reverse("api:oauth2_authorization_server:oauth-user-info", args=[tenant.uuid]),
            'authorize': host+reverse("api:oauth2_authorization_server:authorize", args=[tenant.uuid]),
            'token': host+reverse("api:oauth2_authorization_server:token", args=[tenant.uuid]),
        }
        if algorithm and app.type == 'OIDC':
            uniformed_data['algorithm'] = obj.algorithm
            uniformed_data['logout'] = host+reverse("api:oauth2_authorization_server:oauth-user-logout", args=[tenant.uuid])

        app.data = uniformed_data
        app.save()

    def update(self, tenant, app, data):
        client_type = data.get('client_type')
        redirect_uris = data.get('redirect_uris')
        skip_authorization = data.get('skip_authorization')
        authorization_grant_type = data.get('grant_type')
        algorithm = data.get('algorithm')
        host = get_app_config().get_host()
        obj = Application.objects.filter(name=app.id).first()
        obj.client_type = client_type
        obj.redirect_uris = redirect_uris
        obj.skip_authorization = skip_authorization
        obj.authorization_grant_type = authorization_grant_type
        if algorithm and app.type == 'OIDC':
            obj.algorithm = algorithm
        obj.save()
        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'skip_authorization': obj.skip_authorization,
            'userinfo': host+reverse("api:oauth2_authorization_server:oauth-user-info", args=[tenant.uuid]),
            'authorize': host+reverse("api:oauth2_authorization_server:authorize", args=[tenant.uuid]),
            'token': host+reverse("api:oauth2_authorization_server:token", args=[tenant.uuid]),
        }
        if algorithm and app.type == 'OIDC':
            uniformed_data['algorithm'] = obj.algorithm
            uniformed_data['logout'] = host+reverse("api:oauth2_authorization_server:oauth-user-logout", args=[tenant.uuid])

        app.data = uniformed_data
        app.save()

extension = OAuth2ServerExtension(
    package='com.longgui.oauth2_server',
    description='OAuth2认证服务',
    version='1.0',
    labels='oauth',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)