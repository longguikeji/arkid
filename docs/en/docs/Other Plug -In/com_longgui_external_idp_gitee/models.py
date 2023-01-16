from django.db import models
from django.apps import AppConfig
from arkid.common.model import BaseModel
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract

app_label = 'com_longgui_external_idp_gitee'

class LongguiGiteeAppConfig(AppConfig):

    name = app_label


class GiteeUser(UserExpandAbstract):
    class Meta:
        app_label = app_label

    gitee_user_id = models.CharField(
        max_length=255, blank=True, verbose_name='Gitee ID'
    )
    gitee_nickname = models.CharField(
        max_length=255, blank=True, default='', verbose_name='昵称',
    )
    gitee_avatar = models.CharField(
        max_length=255, blank=True, default='', verbose_name='头像',
    )
