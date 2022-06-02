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


package = 'com.longgui.account.life.arkid'


select_user_page = pages.TablePage(select=True, name=_("Select User", "选择用户"))

pages.register_front_pages(select_user_page)

select_user_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=actions.FrontActionMethod.GET,
    ),
)


class UserExpirationSchema(Schema):
    user: str = Field(
        title=_("Username", "用户名"),
        field="id",
        page=select_user_page.tag,
        link="username",
        type="string",
        show="username",
    )
    username: str = Field(
        default="", title=_("Username", "用户名"), readonly=True, hidden=True
    )
    expiration_time: datetime = Field(title=_("Expiration Time", "过期时间"))

    class Config:
        title = _("User Expiration Setting", "用户过期设置")


class UserExpirationListSchema(Schema):
    __root__: List[UserExpirationSchema] = Field(
        title=_("User Expiration Setting", "用户过期设置"), format="dynamic"
    )

    class Config:
        title = _("User Expiration Setting", "用户过期设置")


class AccountLifeArkIDExtension(AccountLifeExtension):
    def load(self):
        super().load()
        self.register_account_life_schema(UserExpirationListSchema, "user_expiration")

    def create_tenant_config(self, tenant, config, name, type):
        config_created = TenantExtensionConfig()
        config_created.tenant = tenant
        config_created.extension = Extension.active_objects.get(package=self.package)
        for item in config.get('__root__'):  # 解决datetime不能json序列化
            item["expiration_time"] = item["expiration_time"].strftime(
                '%Y-%m-%d %H:%M:%S'
            )
            item["username"] = User.valid_objects.get(id=item["user"]).username
        config_created.config = config.get('__root__')
        config_created.name = name
        config_created.type = type
        config_created.save()
        return config_created

    def update_tenant_config(self, id, config, name, type):
        tenantextensionconfig = TenantExtensionConfig.valid_objects.filter(
            id=id
        ).first()
        for item in config.get('__root__'):  # 解决datetime不能json序列化
            item["expiration_time"] = item["expiration_time"].strftime(
                '%Y-%m-%d %H:%M:%S'
            )
            item["username"] = User.valid_objects.get(id=item["user"]).username
        tenantextensionconfig.config = config.get('__root__')
        tenantextensionconfig.name = name
        tenantextensionconfig.type = type
        tenantextensionconfig.save()
        return tenantextensionconfig

    def periodic_task(self, event, **kwargs):
        logger.info("Doing account life arkid priodic task...")
        configs = self.get_tenant_configs(event.tenant)
        for cfg in configs:
            for item in cfg.config:
                user_id = item.get('user')
                user = User.objects.get(id=user_id)
                expiration_time = timezone.datetime.strptime(
                    item.get('expiration_time'), '%Y-%m-%d %H:%M:%S'
                )
                logger.info(f"expiration_time: {expiration_time}/now: {datetime.now()}")
                if expiration_time <= datetime.now():
                    user.offline()


extension = AccountLifeArkIDExtension(
    package=package,
    name='默认账号生命周期管理',
    version='1.0',
    labels='account-life-arkid',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)
