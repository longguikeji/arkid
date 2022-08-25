import json
from pathlib import Path
from typing import Optional
from django.http import FileResponse
from ninja import Field
from arkid.core.api import GlobalAuth, operation
from arkid.core.constants import *
from arkid.core.extension import create_extension_schema
from arkid.core.translation import gettext_default as _
from arkid.config import get_app_config
from arkid.core.extension.logging import LoggingExtension
from .models import Log


MysqlLoggingSchema = create_extension_schema(
    "MysqlLoggingSchema",
    __file__,
    fields = [
        ('use_local_django_db', Optional[bool], Field(title=_("Use Local Django DB", "使用Django数据库"), default=True)),
        ('host', Optional[str], Field(title=_("Host", "域名或IP地址"))),
        ('port', Optional[str], Field(title=_("Port", "端口"))),
        ('username', Optional[str], Field(title=_("Username", "用户名"))),
        ('password', Optional[str], Field(title=_("Password", "密码"))),
        ('database', Optional[str], Field(title=_("Database", "数据库"))),
    ]
)


class MysqlLoggingExtension(LoggingExtension):

    def load(self):
        self.register_profile_schema(MysqlLoggingSchema)
        super().load()

    def process_log_data(self, data):
        pass
        # print(f_key)
        # extension = self.model
        # storage_path = extension.profile.get('use_local_django_db', True)
        
    def save(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        response = event.response
        user = request.user
        data = event.data
        print("request and response logging data: ", data)
        Log.objects.create(
            tenant=tenant,
            user=user,
            data=data
        )


extension = MysqlLoggingExtension()