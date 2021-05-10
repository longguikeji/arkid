from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from inventory.models import User
from tenant.models import Tenant


class MiniProgramConfig(AppConfig):

    name = 'miniprogram'


class MiniProgramUser(BaseModel):

    class Meta:

        app_label = 'miniprogram'

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.OneToOneField(User, verbose_name='用户', related_name='miniprogram_user', on_delete=models.PROTECT)
    miniprogram_user_id = models.CharField(max_length=255, blank=True, verbose_name='MiniProgram ID')
    name = models.CharField(max_length=128, default='', null=True, blank=True, verbose_name='昵称')
    avatar = models.CharField(max_length=300, default='', null=True, blank=True, verbose_name='头像')
