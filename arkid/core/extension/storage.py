
from abc import abstractmethod
import uuid
from arkid.common.logger import logger
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.event import READ_FILE, SAVE_FILE


class StorageExtension(Extension):

    TYPE = "storage"

    @property
    def type(self):
        return StorageExtension.TYPE

    def load(self):
        super().load()
        self.listen_event(SAVE_FILE, self.event_save_file)
        self.listen_event(READ_FILE, self.event_read_file)

    def event_save_file(self, event, **kwargs):
        tenant = event.tenant
        file = event.data["file"]
        f_key = self.generate_key(file.name)
        self.save_file(file, f_key, event)
        return self.resolve(f_key, tenant, event)
    
    def event_read_file(self,event,**kwargs):
        file_url = event.data["url"]
        return self.read(tenant_id=event.tenant.id,file_url=file_url,**kwargs)

    @abstractmethod
    def save_file(self, file, f_key: str, **kwargs):
        """保存文件

        Args:
            file (File): 文件对象
            f_key (str): 存储文件名称
        """
        pass

    @abstractmethod
    def resolve(self, f_key: str, tenant, **kwargs):
        """生成文件链接

        Args:
            f_key (str): 存储文件名称
            tenant (Tenant): 租户
        """
        pass
    
    @abstractmethod
    def read(self,file_url: str,**kwargs):
        """通过文件链接读取文件数据

        Args:
            file_url (str): 文件链接
        """
        pass
        

    def generate_key(self, file_name: str):
        """生成存储文件名

        Args:
            file_name (str): 原始文件名，用于获取文件后缀

        Returns:
            str: 文件名
        """
        key = '{}.{}'.format(
            uuid.uuid4().hex,
            file_name.split('.')[-1],
        )
        return key
