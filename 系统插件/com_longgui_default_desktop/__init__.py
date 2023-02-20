import json
from arkid.core import extension
from arkid.core.translation import gettext_default as _
from .models import DefaultDesktop
from typing import List, Optional
from pydantic import Field


class DefaultDesktopExtension(extension.Extension):

    def load(self):
        super().load()
        from api.v1.schema.tenant import TenantConfigItemOut, TenantConfigUpdateIn, TenantItemOut, DefaultTenantItemOut
        from api.v1.views.loginpage import LoginPageTenantSchema
        self.register_extend_api(
            TenantConfigItemOut,
            TenantConfigUpdateIn,
            TenantItemOut,
            DefaultTenantItemOut,
            LoginPageTenantSchema,
            default_desktop=(Optional[str], Field(
                title=_("默认桌面路径")))
        )

        self.listen_event("api_v1_views_tenant_get_tenant", self.get_default_desktop)
        self.listen_event("api_v1_views_tenant_get_tenant_config", self.get_default_desktop)
        self.listen_event("api_v1_views_tenant_default_tenant", self.get_default_desktop)

        self.listen_event("api_v1_views_loginpage_login_page", self.login_page_event)

        self.listen_event("api_v1_views_tenant_update_tenant_config",self.update_tenant_config_event)

    
    def get_default_desktop(self,event,*argc, **kwargs):
        default_desktop,_ = DefaultDesktop.active_objects.get_or_create(target=event.tenant)
        event.response["data"]["default_desktop"] = default_desktop.default_desktop

    def login_page_event(self,event,*argc, **kwargs):
        default_desktop,_ = DefaultDesktop.active_objects.get_or_create(target=event.tenant)
        event.response["tenant"]["default_desktop"] = default_desktop.default_desktop

    def update_tenant_config_event(self,event,*argc, **kwargs):
        data = event.request.POST or json.load(event.request.body)
        default_desktop,_ = DefaultDesktop.active_objects.get_or_create(target=event.tenant)
        default_desktop.default_desktop = data.get("default_desktop",default_desktop.default_desktop)
        default_desktop.save()


extension = DefaultDesktopExtension()
