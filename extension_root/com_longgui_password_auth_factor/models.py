from django.db import models
from django.apps import AppConfig
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_password_auth_factor"

class LongguiPasswordAppConfig(AppConfig):

    name = app_label


class UserPassword(create_expand_abstract_model(UserExpandAbstract,app_label,'UserPassword')):
    class Meta:

        app_label = app_label

    password = models.CharField(_("Password", "密码"), max_length=256)
