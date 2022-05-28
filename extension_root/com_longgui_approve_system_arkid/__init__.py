from arkid.core.extension.approve_system import ApproveSystemExtension
from arkid.core.extension import create_extension_schema
from arkid.extension.models import TenantExtensionConfig, TenantExtension
import urllib.parse
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja import Schema
from .approve_requests_page import page, router
from api.v1.pages.approve_manage import router as approve_manage_router

package = 'com.longgui.approve.system.arkid'


class ApproveSystemConfigSchema(Schema):
    description: str = Field(
        title=_('Arpprove System Description', '审批系统描述'), default=''
    )


ApproveSystemArkIDConfigSchema = create_extension_schema(
    'ApproveSystemArkIDConfigSchema', package, base_schema=ApproveSystemConfigSchema
)


class ApproveSystemArkIDExtension(ApproveSystemExtension):
    def load(self):
        # 加载url地址
        # self.load_urls()
        # 加载相应的配置文件
        super().load()
        self.register_approve_system_schema(ApproveSystemArkIDConfigSchema, self.type)
        self.register_front_pages(page)
        approve_manage_router.children.append(router)

    def create_approve_system_config(self, event, **kwargs):
        return super().create_approve_system_config(event, **kwargs)


extension = ApproveSystemArkIDExtension(
    package=package,
    name='默认审批系统',
    version='1.0',
    labels='approve-system-arkid',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)
