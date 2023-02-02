import random
from typing import Optional
from ninja import Field, Schema
from arkid.core import actions, extension, pages
from arkid.core.error import ErrorCode
from arkid.core.extension import create_extension_schema
from arkid.core.event import CREATE_USER, SEND_SMS, USER_REGISTER, Event, dispatch_event
from arkid.core.models import User
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig
from .schema import *
from django.contrib.auth.hashers import (
    make_password,
)


class AutoPasswordExtension(extension.Extension):

    def load(self):
        super().load()
        self.create_extension_config_schema()
        self.listen_event(CREATE_USER, self.auto_create_password)
        self.listen_event(USER_REGISTER, self.register_user_password)

    def get_current_config(self, tenant):
        return TenantExtensionConfig.valid_objects.filter(tenant=tenant, extension=self.model).first()

    def random_password(self, length=8):
        random_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!@#"
        return ''.join(random.choice(random_str) for _ in range(length))

    def auto_password(self, user, password):
        user.password = make_password(password)
        user.save()

    def send_sms(self, tenant, request, config_id, package, mobile, areacode, password, username, template_param_key="password"):
        responses = dispatch_event(
            Event(
                tag=SEND_SMS,
                tenant=tenant,
                request=request,
                data={
                    "config_id": config_id,
                    "mobile": mobile,
                    template_param_key: password,
                    "areacode": areacode,
                    "username": username,
                },
                packages=package
            )
        )

    def register_user_password(self, event, *argc, **kwargs):
        if (not isinstance(event.data, User)):
            return
        user = User.expand_objects.get(id=event.data.id)
        if (not user["mobile"]) or user["password"]:
            print("no mobile or password was set")
            return

        config = self.get_current_config(event.tenant)
        password = self.random_password(config.config.get('code_length', 8))

        self.auto_password(event.data, password)

        self.send_sms(event.tenant, event.request, config.config["sms_config"]["id"], config.config["sms_config"]
                      ["package"], user["mobile"], '86', password, event.request.user.username if event.request.user else "", config.config.get("template_param_key", "password"))

    def auto_create_password(self, event, *argc, **kwargs):

        user = User.expand_objects.get(id=event.data.id)

        if not user["mobile"]:
            print("no mobile")
            return

        config = self.get_current_config(event.tenant)
        password = self.random_password(config.config.get('code_length', 8))

        self.auto_password(event.data, password)

        self.send_sms(event.tenant, event.request, config.config["sms_config"]["id"], config.config["sms_config"]
                      ["package"], user["mobile"], '86', password, event.request.user.username if event.request.user else "", config.config.get("template_param_key", "password"))

    def create_extension_config_schema(self):
        """创建插件运行时配置schema描述
        """
        select_sms_page = pages.TablePage(select=True, name=_("指定短信插件运行时"))

        self.register_front_pages(select_sms_page)

        select_sms_page.create_actions(
            init_action=actions.DirectAction(
                path='/api/v1/tenants/{tenant_id}/config_select/?extension__type=sms',
                method=actions.FrontActionMethod.GET
            )
        )

        AutoPasswordSchema = create_extension_schema(
            'AutoPasswordSchema',
            __file__,
            [
                (
                    'sms_config',
                    AutoPasswordSchemaConfigSchema,
                    Field(
                        title=_('sms extension config', '短信插件运行时'),
                        page=select_sms_page.tag,
                    ),
                ),
                (
                    'code_length',
                    int,
                    Field(
                        title=_('code_length', '密码长度'),
                        default=6
                    )
                ),
                (
                    'template_param_key',
                    str,
                    Field(
                        title=_('template_param_key', '模板参数名称'),
                        default="password"
                    )
                ),
            ],
            Schema,
        )
        self.register_config_schema(AutoPasswordSchema, self.package)


extension = AutoPasswordExtension()
