
from abc import abstractmethod
import uuid
from arkid.common.logger import logger
from ninja import Schema
from typing import List, Optional, Literal
from pydantic import Field
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.models import StorageData
from arkid.core import translation as core_translation
from arkid.core.event import SAVE_FILE


class StorageExtension(Extension):

    TYPE = "storage"

    @property
    def type(self):
        return StorageExtension.TYPE

    def load(self):
        super().load()
        self.listen_event(SAVE_FILE, self.event_save_file)

    def event_save_file(self, event, **kwargs):
        tenant = event.tenant
        file = event.data["file"]
        f_key = self.generate_key(file.name)
        self.save_file(file, f_key, event)
        return self.resolve(f_key, tenant, event)

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

    def generate_key(self, file_name: str):
        key = '{}.{}'.format(
            uuid.uuid4().hex,
            file_name.split('.')[-1],
        )
        return key
