from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.core.models import UserExpandAbstract

from django.contrib.auth.models import User

app_label = "com_longgui_app_cas_server"

class LongguiCasServerAppConfig(AppConfig):
    name = app_label
    
class UserLastLogin(UserExpandAbstract):
    class Meta:
        app_label = app_label
    
    last_login = models.DateTimeField(_('last login', '最后登录时间'), blank=True, null=True)