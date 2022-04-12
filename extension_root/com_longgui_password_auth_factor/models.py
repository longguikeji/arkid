from django.db import models
from django.apps import AppConfig
from arkid.core.expand import UserExpandAbstract
from arkid.core.translation import gettext_default as _


class LongguiPasswordAppConfig(AppConfig):

    name = "com_longgui_password_auth_factor"


class UserPassword(UserExpandAbstract):
    class Meta:

        app_label = "com_longgui_password_auth_factor"

    password = models.CharField(_("Password", "密码"), max_length=40)
    # package = models.CharField(_("Package", "包"), max_length=40)
