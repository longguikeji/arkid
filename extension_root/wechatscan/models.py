from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from inventory.models import User
from tenant.models import Tenant


class WeChatScanAppConfig(AppConfig):

    name = "wechatscan"


class WeChatScanUser(BaseModel):

    class Meta:

        app_label = "wechatscan"

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.OneToOneField(User, verbose_name="用户", related_name="wechatscan_user", on_delete=models.PROTECT)
    openid = models.CharField(max_length=256, default='', null=True, blank=True, verbose_name="openid")


class WeChatScanInfo(BaseModel):

    class Meta:
        app_label = "wechatscan"

    openid = models.CharField(max_length=256, default='', null=True, blank=True, verbose_name="openid")
    access_token = models.CharField(max_length=256, default='', null=True, blank=True, verbose_name='access_token')
    refresh_token = models.CharField(max_length=256, default='', null=True, blank=True, verbose_name='refresh_token')
    unionid = models.CharField(max_length=256, default='', null=True, blank=True, verbose_name="unionid(需要客户在开放平台打通了多个公众号)")
    nickname = models.CharField(max_length=128, default='', null=True, blank=True, verbose_name='昵称')
    avatar = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name='头像')
