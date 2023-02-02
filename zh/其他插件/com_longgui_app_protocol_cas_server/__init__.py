from django.urls import reverse
from django.conf import settings
from arkid.config import get_app_config
from arkid.core.extension.app_protocol import AppProtocolExtension
from .appscheme import (
    CasConfigSchema,
)

from .mama_cas.urls import urlpatterns as urls
from arkid.core.extension import create_extension_schema
from .mama_cas.views import LoginView as AuthorizationView

CasConfigSchema = create_extension_schema('CasConfigSchema',__file__, base_schema=CasConfigSchema)

class CasServerExtension(AppProtocolExtension):

    def load(self):
        # 加载url地址
        self.load_urls()
        # 加载相应的view
        self.load_auth_view()
        # 加载相应的配置文件
        self.register_app_protocol_schema(CasConfigSchema, 'CAS')
        super().load()

    def load_urls(self):
        self.register_routers(urls, True)

    def load_auth_view(self):
        # 加载认证view
        auth_view = AuthorizationView.as_view()
        auth_path = r"app/(?P<app_id>[\w-]+)/cas/login/$"
        url_name = "cas_login"
        type = ['CAS']
        self.register_enter_view(auth_view, auth_path, url_name, type)

    def create_app(self, event, **kwargs):
        config = event.data["config"]
        return self.update_app_data(event, config, True)

    def update_app(self, event, **kwargs):
        config = event.data["config"]
        return self.update_app_data(event, config, False)

    def delete_app(self, event, **kwargs):
        return True

    def update_app_data(self, event, config, is_create):
        '''
        修改应用程序
        '''
        app = event.data["app"]
        tenant = event.tenant
        self.update_url_data(tenant.id, config, app.id)
        return True

    def update_url_data(self, tenant_id, config, app_id):
        '''
        更新配置中的url信息
        '''
        front_host = get_app_config().get_frontend_host()
        host = get_app_config().get_host()
        namespace = f'api:{self.pname}_tenant'
        config["login"] = front_host+reverse(namespace+":cas_login", args=[tenant_id, app_id])
        # config["logout"] = host+reverse(namespace+":cas_logout", args=[tenant_id, app_id])
        config["logout"] = host+reverse(namespace+":cas_logout", args=[tenant_id, app_id])
        config["service_validate"] = host+reverse(namespace+":cas_service_validate", args=[tenant_id, app_id])
        config["proxy_validate"] = host+reverse(namespace+":cas_proxy_validate", args=[tenant_id, app_id])
        config["proxy"] = host+reverse(namespace+":cas_proxy", args=[tenant_id, app_id])
        config["p3_service_validate"] = host+reverse(namespace+":cas_p3_service_validate", args=[tenant_id, app_id])
        config["p3_proxy_validate"] = host+reverse(namespace+":cas_p3_proxy_validate", args=[tenant_id, app_id])
        config["warn"] = host+reverse(namespace+":cas_warn", args=[tenant_id, app_id])
        config["saml_validate"] = host+reverse(namespace+":cas_saml_validate", args=[tenant_id, app_id])

extension = CasServerExtension()