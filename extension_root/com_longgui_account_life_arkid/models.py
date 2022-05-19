from django.db import models
from django.apps import AppConfig
from arkid.core.expand import UserExpandAbstract
from arkid.core.translation import gettext_default as _


class LongguiAccountLifeArkidAppConfig(AppConfig):

    name = "com_longgui_account_life_arkid"


class UserExpiration(UserExpandAbstract):
    class Meta:

        app_label = "com_longgui_account_life_arkid"

    expiration_time = models.DateTimeField(blank=True, null=True, verbose_name='过期时间')
