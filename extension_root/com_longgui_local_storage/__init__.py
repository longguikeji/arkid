from pathlib import Path
import uuid
from django.urls import reverse
from ninja import Field
from typing import Optional
from types import SimpleNamespace
from arkid.core import event
from arkid.core.extension import Extension, create_extension_schema
from arkid.core.event import SAVE_FILE
from arkid.core.translation import gettext_default as _
from alibabacloud_dysmsapi20170525.client import Client
from alibabacloud_tea_openapi import models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models

package = 'com.longgui.local_storage'

SettingsSchema = create_extension_schema(
    "LocalStorageSettingsSchema",
    package,
    fields = [
        ('storage_path', str, Field(title=_("Storage Path", "存储路径"))),
    ]
)


class LocalStorageExtension(Extension):

    def load(self):
        self.listen_event(SAVE_FILE, self.save_file)
        self.register_settings_schema(SettingsSchema)
        super().load()

    def save_file(self, event, **kwargs):
        tenant = event.tenant
        file = event.data["file"]

        settings = self.get_tenant_settings(tenant)
        settings = SimpleNamespace(**settings.settings)
        
        key = self.generate_key(key)
        p = Path(settings.data_path) / key

        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        with open(p, 'wb') as fp:
            for chunk in file.chunks():
                fp.write(chunk)

        return self.resolve(key)
    
    def resolve(self, key):
        return reverse("api:local_storage:render", args=[key, ])
    
    def generate_key(self, file_name:str):
        key = '{}.{}'.format(
            uuid.uuid4().hex,
            file_name.split('.')[-1],
        )
        return key


extension = LocalStorageExtension(
    package=package,
    name='本地文件存储',
    version='1.0',
    labels='storage',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)