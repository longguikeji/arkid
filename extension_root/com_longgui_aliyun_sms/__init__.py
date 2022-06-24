from ninja import Field
from typing import Optional
from types import SimpleNamespace
from arkid.core import event
from arkid.core.extension import Extension, create_extension_schema_by_package
from arkid.core.event import SEND_SMS
from arkid.core.translation import gettext_default as _
from alibabacloud_dysmsapi20170525.client import Client
from alibabacloud_tea_openapi import models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models

package = 'com.longgui.aliyun_sms'

SettingsSchema = create_extension_schema_by_package(
    'SettingsSchema',
    package,
    fields = [
        ('access_key_id', str, Field(title=_("AccessKey ID"))),
        ('access_key_secret', str, Field(title=_("AccessKey Secret"))),
        ('region_id', Optional[str], Field(title=_("Region ID", "地域ID"))),
        ('endpoint', Optional[str], Field(title=_("Endpoint", "访问的域名"))),
    ]
)


ConfigSchema = create_extension_schema_by_package(
    "ConfigSchema",
    package,
    fields = [
        ('sign_name', str, Field(title=_("Sign Name", "短信签名名称"))),
        ('template_code', str, Field(title=_("Template Code", "短信模板CODE"))),
        ('sms_up_extend_code', Optional[str], Field(title=_("Sms Up Extend Code", "上行短信扩展码"))),
        ('out_id', Optional[str], Field(title=_("Out ID", "外部流水扩展字段"))),
    ]
)


class AliyunSMSExtension(Extension):

    def load(self):
        self.listen_event(SEND_SMS, self.send_sms)
        self.register_settings_schema(SettingsSchema)
        self.register_config_schema(ConfigSchema)
        super().load()

    def send_sms(self, event, **kwargs):
        tenant = event.tenant
        config_id = event.data["config_id"]
        template_params = event.data["template_params"]
        phone_number = event.data["phone_number"]
        
        settings = self.get_tenant_settings(tenant)
        settings = SimpleNamespace(**settings.settings)
        
        config = self.get_config_by_id(config_id).config
        config = SimpleNamespace(**config)

        aliyun_config = models.Config(
            # 您的AccessKey ID,
            access_key_id=settings.access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=settings.access_key_secret,
            # 地域ID
            region_id=settings.region_id or None,
            # 访问的域名
            endpoint=settings.endpoint or None,
        )

        client = Client(aliyun_config)
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=phone_number,
            sign_name=config.sign_name,
            template_code=config.template_code,
            template_param=template_params,
            sms_up_extend_code=config.sms_up_extend_code or None,
            out_id=config.out_id or None,
        )
        res = client.send_sms(send_sms_request)
        return res.body.to_map()


extension = AliyunSMSExtension(
    package=package,
    name='阿里云短信',
    version='1.0',
    labels='sms',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)