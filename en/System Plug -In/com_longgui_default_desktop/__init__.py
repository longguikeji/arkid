from arkid.core import extension
from arkid.core.translation import gettext_default as _
from .models import DefaultDesktop
from typing import List, Optional
from pydantic import Field


class DefaultDesktopExtension(extension.Extension):

    def load(self):
        super().load()
        self.register_extend_field(DefaultDesktop, 'default_desktop')
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


extension = DefaultDesktopExtension()
