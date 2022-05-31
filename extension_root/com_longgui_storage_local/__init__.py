from pathlib import Path
import uuid
from django.urls import reverse
from ninja import Field
from arkid.core.extension import Extension, create_extension_schema
from arkid.core.event import SAVE_FILE
from arkid.core.translation import gettext_default as _
from arkid.config import get_app_config
from . import views

package = 'com.longgui.storage.local'

ProfileSchema = create_extension_schema(
    "LocalStorageProfileSchema",
    package,
    fields = [
        ('storage_path', str, Field(title=_("Storage Path", "存储路径"))),
    ]
)


class LocalStorageExtension(Extension):

    def load(self):
        self.listen_event(SAVE_FILE, self.save_file)
        self.register_profile_schema(ProfileSchema)
        super().load()

    def save_file(self, file, f_key):
        extension = self.model()
        storage_path = extension.profile.get('storage_path','./storage/')
        
        p = Path(storage_path) / f_key

        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        with open(p, 'wb') as fp:
            for chunk in file.chunks():
                fp.write(chunk)
                
    def resolve(self, f_key, tenant):
        host = get_app_config().get_frontend_host()
        return f'{host}/api/v1/tenant/{tenant.id}/localstorage/{f_key}'
    
    


extension = LocalStorageExtension(
    package=package,
    name='本地文件存储',
    version='1.0',
    labels='storage',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)