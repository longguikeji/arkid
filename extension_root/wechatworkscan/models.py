from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from inventory.models import User
from tenant.models import Tenant


class WeChatWorkScanAppConfig(AppConfig):

    name = "wechatworkscan"


class WeChatWorkScanUser(BaseModel):

    class Meta:

        app_label = "wechatworkscan"

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.OneToOneField(User, verbose_name="用户", related_name="wechatworkscan_user", on_delete=models.PROTECT)
    work_user_id = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name="openid")


class WeChatWorkScanInfo(BaseModel):

    class Meta:
        app_label = "wechatworkscan"

    work_user_id = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name="user_id")
    access_token = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name='access_token')
    device_id = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name="设备id")
