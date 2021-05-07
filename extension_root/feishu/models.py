from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from inventory.models import User
from tenant.models import Tenant


class FeishuConfig(AppConfig):

    name = 'feishu'


class FeishuUser(BaseModel):

    class Meta:

        app_label = 'feishu'

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.OneToOneField(
        User, verbose_name='用户', related_name='feishu_user', on_delete=models.PROTECT
    )
    feishu_user_id = models.CharField(
        max_length=255, blank=True, verbose_name='Feishu ID'
    )
