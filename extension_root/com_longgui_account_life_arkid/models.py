from django.db import models
from django.apps import AppConfig
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_account_life_arkid"

class LongguiAccountLifeArkidAppConfig(AppConfig):

    name = app_label


class UserExpiration(create_expand_abstract_model(UserExpandAbstract,app_label,'UserExpiration')):
    class Meta:
        app_label = app_label

    expiration_time = models.DateTimeField(blank=True, null=True, verbose_name='过期时间')
