from arkid.core.extension.approve_system import ApproveSystemExtension
from arkid.core.extension import create_extension_schema
from arkid.extension.models import TenantExtensionConfig, TenantExtension
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja import Schema
from .approve_requests_page import router_page, waiting_page, approved_page, router
from api.v1.pages.approve_manage import router as approve_manage_router
from . import views
from arkid.core.extension.approve_system import ApproveSystemBaseSchema
from arkid.core.approve import restore_approve_request
from arkid.common.logger import logger
from api.v1.schema.approve_request import (
    ApproveRequestListItemOut,
    ApproveRequestListOut,
)
from arkid.core.pagenation import CustomPagination
from arkid.core.models import ApproveRequest
from arkid.core.constants import *
from arkid.core.api import api, operation
from ninja.pagination import paginate
from typing import List


class ApproveSystemArkIDSchema(ApproveSystemBaseSchema):
    pass


ApproveSystemArkIDConfigSchema = create_extension_schema(
    'ApproveSystemArkIDConfigSchema', __file__, base_schema=ApproveSystemArkIDSchema
)


class ApproveSystemArkIDExtension(ApproveSystemExtension):
    def load(self):
        super().load()
        self.register_api(
            f'/approve_requests/',
            'GET',
            self.list_tenant_approve_requests,
            response=List[ApproveRequestListItemOut],
            tenant_path=True,
        )
        self.register_approve_system_schema(
            ApproveSystemArkIDConfigSchema, 'approve_system_arkid'
        )
        self.register_front_pages([router_page, waiting_page, approved_page])
        self.register_front_routers(router, approve_manage_router)

    @operation(List[ApproveRequestListItemOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    @paginate(CustomPagination)
    def list_tenant_approve_requests(
        self, request, tenant_id: str, is_approved: str = ''
    ):
        package = 'com.longgui.approve.system.arkid'
        requests = ApproveRequest.valid_objects.filter(
            tenant=request.tenant, action__extension__package=package
        )
        if is_approved == 'true':
            requests = requests.exclude(status="wait")
        elif is_approved == 'false':
            requests = requests.filter(status="wait")
        return requests

    def create_approve_request(self, event, **kwargs):
        pass

    def pass_approve_request(self, request, approve_request):
        response = restore_approve_request(approve_request)
        logger.info(f'Restore approve request with result: {response}')

    def deny_approve_request(self, request, approve_request):
        pass


extension = ApproveSystemArkIDExtension()
