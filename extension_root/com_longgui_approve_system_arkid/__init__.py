from arkid.core.extension.approve_system import ApproveSystemExtension
from arkid.core.extension import create_extension_schema
from arkid.extension.models import TenantExtensionConfig, TenantExtension

from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja import Schema
from .approve_requests_page import page, router
from api.v1.pages.approve_manage import router as approve_manage_router
from . import views
from arkid.core.extension.approve_system import ApproveSystemBaseSchema

package = 'com.longgui.approve.system.arkid'


class ApproveSystemArkIDSchema(ApproveSystemBaseSchema):
    pass


ApproveSystemArkIDConfigSchema = create_extension_schema(
    'ApproveSystemArkIDConfigSchema', package, base_schema=ApproveSystemArkIDSchema
)


class ApproveSystemArkIDExtension(ApproveSystemExtension):
    def load(self):
        super().load()
        self.register_approve_system_schema(ApproveSystemArkIDConfigSchema, self.type)
        approve_manage_router.children.append(router)

    def change_approve_request_status(self, request, approve_request_id):
        pass

    def create_approve_request(self, event, **kwargs):
        pass


extension = ApproveSystemArkIDExtension(
    package=package,
    name='默认审批系统',
    version='1.0',
    labels='approve-system-arkid',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)
