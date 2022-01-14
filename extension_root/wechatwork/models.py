from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from inventory.models import User
from tenant.models import Tenant


class WeChatWorkAppConfig(AppConfig):

    name = "wechatwork"


class WeChatWorkUser(BaseModel):

    class Meta:

        app_label = "wechatwork"

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.OneToOneField(User, verbose_name="用户", related_name="wechatwork_user", on_delete=models.PROTECT)
    work_user_id = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name="openid")


class WeChatWorkInfo(BaseModel):

    class Meta:
        app_label = "wechatwork"

    work_user_id = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name="user_id")
    access_token = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name='access_token')
    device_id = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name="设备id")
