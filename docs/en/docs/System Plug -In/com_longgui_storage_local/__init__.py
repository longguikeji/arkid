from pathlib import Path
from typing import Optional
from django.http import FileResponse
from ninja import Field
from arkid.core.api import GlobalAuth, operation
from arkid.core.constants import *
from arkid.core.extension import create_extension_schema
from arkid.core.translation import gettext_default as _
from arkid.config import get_app_config
from arkid.core.extension.storage import StorageExtension

ProfileSchema = create_extension_schema(
    "LocalStorageProfileSchema",
    __file__,
    fields = [
        ('storage_path', Optional[str], Field(title=_("Storage Path", "存储路径"),default=_("/data"))),
    ]
)
class LocalStorageExtension(StorageExtension):

    def load(self):
        self.register_profile_schema(ProfileSchema)
        
        self.register_api(
            "/localstorage/{file_name}",
            'GET',
            self.get_file,
            tenant_path=True,
            auth=None
        )
        
        super().load()

    def save_file(self, file, f_key, response=None, *args, **kwargs):
        print(f_key)
        extension = self.model
        storage_path = extension.profile.get('storage_path','/data')
        
        p = Path(storage_path) / f_key

        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        with open(p, 'wb') as fp:
            for chunk in file.chunks() if file else response:
                fp.write(chunk)
                
    def resolve(self, f_key, tenant, *args, **kwargs):
        host = get_app_config().get_frontend_host()
        return f'{host}/api/v1/tenant/{tenant.id}/com_longgui_storage_local/localstorage/{f_key}'
    
    
    def get_file(self, request, tenant_id: str, file_name:str):
        """ 本地存储插件获取文件
        """
        extension = self.model
        storage_path = extension.profile.get('storage_path','/data')
        file_path = Path(storage_path) / file_name
        
        return FileResponse(
            open(file_path, 'rb')
        )
        
    def read(self,tenant_id,file_url,**kwargs):
        """读取文件数据

        Args:
            tenant_id (str): 租户ID
            file_url (str): 文件链接

        Returns:
            bytes: 文件数据
        """
        host = get_app_config().get_frontend_host()
        useless_part = f'{host}/api/v1/tenant/{tenant_id}/com_longgui_storage_local/localstorage/'
        file_name = file_url.replace(useless_part, "")
        extension = self.model
        storage_path = extension.profile.get('storage_path','/data')
        file_path = Path(storage_path) / file_name
        rs = None
        
        with open(file_path,"rb") as f:
            rs = f.read()
        
        return rs
        

extension = LocalStorageExtension()