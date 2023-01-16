from django.urls import reverse
from django.conf import settings
from arkid.config import get_app_config
from arkid.core.extension.app_protocol import AppProtocolExtension
from .appscheme import (
    Oauth2ConfigSchema, OIDCConfigSchema,
)
from oauth2_provider.models import Application
from oauth2_provider.urls import urlpatterns as urls
from arkid.core.extension import create_extension_schema
from oauth2_provider.views.base import AuthorizationView

OIDCConfigSchema = create_extension_schema('OIDCConfigSchema',__file__, base_schema=OIDCConfigSchema)
Oauth2ConfigSchema = create_extension_schema('Oauth2ConfigSchema',__file__, base_schema=Oauth2ConfigSchema)

class OAuth2ServerExtension(AppProtocolExtension):

    def load(self):
        # 加载url地址
        self.load_urls()
        # 加载相应的view
        self.load_auth_view()
        # 加载相应的配置文件
        if not settings.IS_CENTRAL_ARKID:
            self.register_app_protocol_schema(OIDCConfigSchema, 'OIDC')
            self.register_app_protocol_schema(Oauth2ConfigSchema, 'OAuth2')
        super().load()

    def load_urls(self):
        self.register_routers(urls, True)
    
    def load_auth_view(self):
        # 加载认证view
        auth_view = AuthorizationView.as_view()
        auth_path = r"app/(?P<app_id>[\w-]+)/oauth/authorize/$"
        url_name = "authorize"
        type = ['OIDC', 'OAuth2']
        self.register_enter_view(auth_view, auth_path, url_name, type)

    def create_app(self, event, **kwargs):
        config = event.data["config"]
        return self.update_app_data(event, config, True)

    def update_app(self, event, **kwargs):
        config = event.data["config"]
        return self.update_app_data(event, config, False)

    def delete_app(self, event, **kwargs):
        Application.objects.filter(uuid=event.data.id).delete()
        return True

    def update_app_data(self, event, config, is_create):
        '''
        修改应用程序
        '''
        app = event.data["app"]
        tenant = event.tenant

        client_type = config["client_type"]
        redirect_uris = config["redirect_uris"]
        grant_type = config["grant_type"]
        skip_authorization = config["skip_authorization"]
        app_type = event.data.get("app_type")
        algorithm = config.get("algorithm",None)

        obj,iscreated = Application.objects.get_or_create(uuid=app.id)                                                                                
        obj.name = app.name
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
        namespace = f'api:{self.pname}_tenant'
        config["userinfo"] = host+reverse(namespace+":oauth-user-info", args=[tenant_id])
        config["authorize"] = host+reverse(namespace+":authorize", args=[tenant_id, obj.uuid])
        config["token"] = host+reverse(namespace+":token", args=[tenant_id])
        config["logout"] = host+reverse(namespace+":oauth-user-logout", args=[tenant_id])
        config["issuer_url"] = "{}/api/v1/tenant/{}/app/{}".format(host,tenant_id,obj.uuid)
        config["client_id"] = obj.client_id
        config["client_secret"] = obj.client_secret
        config["skip_authorization"] = obj.skip_authorization


extension = OAuth2ServerExtension()