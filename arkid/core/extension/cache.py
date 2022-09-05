
from abc import abstractmethod
from typing import Optional
import uuid
from arkid.common.logger import logger
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.event import CACHE_SET,CACHE_GET


class CacheExtension(Extension):

    TYPE = "cache"

    @property
    def type(self):
        return CacheExtension.TYPE

    def load(self):
        super().load()
        self.listen_event(CACHE_GET, self.event_cache_get)
        self.listen_event(CACHE_SET, self.event_cache_set)

    def event_cache_get(self, event, **kwargs):
        return self.get(
            event.tenant,
            **event.data
        )
    
    def event_cache_set(self,event,**kwargs):
        return self.set(
            tenant=event.tenant,
            **event.data
        )

    @abstractmethod
    def get(self, tenant, key: str, **kwargs):
        """读取

        Args:
            tenant:租户
            key: 存储名称
        """
        pass

    @abstractmethod
    def set(self, tenant, key: str, value:any, **kwargs)-> bool:
        """存储

        Args:
            key (str): 存储名称
            tenant (Tenant): 租户
            value:值
        """
        pass
