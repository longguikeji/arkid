from arkid.core.extension.account_life import AccountLifeExtension
from arkid.core.extension import create_extension_schema
from arkid.extension.models import TenantExtensionConfig, TenantExtension, Extension
from arkid.core.models import User
import urllib.parse
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja import Schema
from api.v1.pages.approve_manage import router as approve_manage_router
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from arkid.common.logger import logger
import json
from api.v1.pages.user_manage import router as user_manage_router
from arkid.core import routers
from datetime import datetime
from typing import List
from arkid.core import pages, actions
from django.utils import dateformat, timezone
from uuid import UUID
from pydantic import UUID4

select_user_page = pages.TablePage(select=True, name=_("Select User", "选择用户"))

# pages.register_front_pages(select_user_page)

select_user_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=actions.FrontActionMethod.GET,
    ),
)


class SelectUserIn(Schema):
    id: UUID4 = Field(hidden=True)
    username: str


class UserExpirationSchema(Schema):
    user: SelectUserIn = Field(
        title=_("Username", "用户名"),
        page=select_user_page.tag,

    )

    expiration_time: datetime = Field(title=_("Expiration Time", "过期时间"))

    class Config:
        title = _("User Expiration Setting", "用户过期设置")


UserExpirationSchema = create_extension_schema(
    'UserExpirationSchema', __file__, base_schema=UserExpirationSchema
)


class UserExpirationListSchema(Schema):
    __root__: List[UserExpirationSchema] = Field(
        title=_("User Expiration Setting", "用户过期设置"), format="dynamic"
    )

    class Config:
        title = _("User Expiration Setting", "用户过期设置")


UserExpirationListSchema = create_extension_schema(
    'UserExpirationListSchema', __file__, base_schema=UserExpirationListSchema
)


class AccountLifeArkIDExtension(AccountLifeExtension):
    def load(self):
        super().load()
        self.register_front_pages(select_user_page)
        self.register_account_life_schema(UserExpirationListSchema, "user_expiration")

    def create_tenant_config(self, tenant, config, name, type):
        """
        创建生命周期配置，手工解决expiration_time类型为datetime不能json序列化的问题
        """
        config_created = TenantExtensionConfig()
        config_created.tenant = tenant
        config_created.extension = Extension.active_objects.get(package=self.package)
        config_created.config = json.loads(config.json())
        config_created.name = name
        config_created.type = type
        config_created.save()
        return config_created

    def update_tenant_config(self, id, config, name, type):
        """
        更新生命周期配置，手工解决expiration_time类型为datetime不能json序列化的问题
        """
        tenantextensionconfig = TenantExtensionConfig.valid_objects.filter(
            id=id
        ).first()

        tenantextensionconfig.config = json.loads(config.json())
        tenantextensionconfig.name = name
        tenantextensionconfig.type = type
        tenantextensionconfig.save()
        return tenantextensionconfig

    def periodic_task(self, event, **kwargs):
        """
        遍历所有插件配置，如果配置中用户对应的过期时间小于当前时间，则禁用用户
        Args:
            event (arkid.core.event.Event):  生命周期定时任务事件
        """
        logger.info("Doing account life arkid priodic task...")
        configs = self.get_tenant_configs(event.tenant)
        for cfg in configs:
            for item in cfg.config:
                user_id = item.get('user').get('id')
                user = User.objects.get(id=user_id)
                expiration_time = timezone.datetime.strptime(
                    item.get('expiration_time'), '%Y-%m-%dT%H:%M:%S'
                )
                logger.info(f"expiration_time: {expiration_time}/now: {datetime.now()}")
                if expiration_time <= datetime.now():
                    user.offline()


extension = AccountLifeArkIDExtension()
