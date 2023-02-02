import json

from arkid.core import extension
from typing import Optional, List
from django.http import FileResponse
from arkid.core.api import operation
from arkid.extension.models import TenantExtension
from arkid.core.translation import gettext_default as _
from arkid.core import pages, actions, routers
from arkid.core.pagenation import CustomPagination
from arkid.core.extension import create_extension_schema
from arkid.core import event as core_event
from arkid.core.schema import ResponseSchema
from ninja.pagination import paginate
from arkid.core.constants import *
from ninja import Field, Schema
from arkid.core import routers

class SystemDocExtension(extension.Extension):

    def load(self):
        self.download_path = self.register_extension_api()
        # 注册schema
        DownloadDocSchema = create_extension_schema(
            "SystemDocSettingsSchema",
            __file__,
            fields = [
                ('download_path', Optional[str], Field(title=_("Click Download", "点击下载"), format='download')),
            ]
        )
        self.register_settings_schema(DownloadDocSchema)
        # self.listen_event("api_v1_views_tenant_extension_get_extension_settings_pre", self.extension_pre)
        self.listen_event("api_v1_views_tenant_extension_get_extension_settings", self.extension_last)
        super().load()
    
    def extension_last(self, event, **kwargs):
        tenant = event.tenant
        response = event.response
        request = event.request
        response_data = response.get('data')
        if response_data.extension.id == self.model.id:
            if response_data.is_active is False:
                response_data.settings = {}
            else:
                settings = response_data.settings
                download_path = settings.get('download_path', '')
                settings['download_path'] = '{}?DOWNLOAD_TOKEN={}'.format(self.download_path, request.auth.token)

    def register_extension_api(self):
        download_path = self.register_api(
            '/download_system_doc/', 
            'GET', 
            self.download_system_doc, 
            tenant_path=True,
        )
        return download_path

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def download_system_doc(self, request, tenant_id:str):
        """ 下载交付文档
        """
        import os
        file_name = 'arkid_system_doc.zip'
        file_path = os.path.join(self.ext_dir, file_name)
        
        return FileResponse(
            open(file_path, 'rb')
        )

extension = SystemDocExtension()