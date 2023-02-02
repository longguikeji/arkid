from django.db import models
from django.apps import AppConfig
from arkid.common.model import BaseModel
from arkid.core.expand import create_expand_abstract_model
from arkid.core.models import UserExpandAbstract

app_label = 'com_longgui_external_idp_miniprogram'

class LongguiMiniprogramAppConfig(AppConfig):

    name = app_label


class MiniprogramUser(UserExpandAbstract):
    class Meta:
        app_label = app_label

    miniprogram_user_id = models.CharField(
        max_length=255, blank=True, verbose_name='Miniprogram ID'
    )
    miniprogram_nickname = models.CharField(
        max_length=255, blank=True, default='', verbose_name='昵称',
    )
    miniprogram_avatar = models.CharField(
        max_length=255, blank=True, default='', verbose_name='头像',
    )
