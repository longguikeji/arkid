from django.db import models
from django.apps import AppConfig
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_auth_factor_email"


class LongguiEmailAppConfig(AppConfig):

    name = app_label


class UserEmail(UserExpandAbstract):
    class Meta:
        app_label = app_label

    email = models.CharField(_("Email", "邮箱账号"), max_length=256,blank=True,null=True)