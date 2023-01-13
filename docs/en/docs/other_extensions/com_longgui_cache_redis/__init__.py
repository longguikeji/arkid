from ninja import Field
from typing import Optional
from arkid.core.extension import create_extension_schema
from arkid.core.extension.cache import CacheExtension
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
import redis

class RedisCacheExtension(CacheExtension):

    def load(self):
        self.register_tenant_settings_schema()
        super().load()
    
    def register_tenant_settings_schema(self):
        redisCacheExtensionSettingsSchema = create_extension_schema(
            "redisCacheExtensionSettingsSchema",
            __file__,
            [
                (
                    "host",
                    str,
                    Field(
                        title=_("服务地址")
                    )
                ),
                (
                    "port",
                    int,
                    Field(
                        title=_("服务端口"),
                        default=3306
                    )
                ),
                (
                    "password",
                    str,
                    Field(
                        title=_("服务密码"),
                        format="password"
                    )
                ),
                (
                    "db",
                    str,
                    Field(
                        title=_("数据库"),
                        default=0
                    )
                ),
            ]
        )
        self.register_settings_schema(
            redisCacheExtensionSettingsSchema
        )
    
    def get(self, tenant, key: str, **kwargs):
        """读取

        Args:
            tenant:租户
            key: 存储名称
        """
        conn = self.get_redis_conn(tenant)
        if conn:
            return conn.get(key)

    def set(self, tenant, key: str, value:any, expired:Optional[int]=None,**kwargs):
        """存储

        Args:
            key (str): 存储名称
            tenant (Tenant): 租户
            value:值
        """
        conn = self.get_redis_conn(tenant)
        if conn:
            conn.set(key,value,ex=expired)
            return True
    
    def get_redis_conn(self,tenant):
        settings = self.get_settings(tenant)
        
        if settings.settings:
            return redis.StrictRedis(
                host=settings.settings.get("host"), 
                port=settings.settings.get("port"), 
                password=settings.settings.get("password",None),
                db=settings.settings.get("db",0),
                decode_responses=True
            )
            
        
    

extension = RedisCacheExtension()
