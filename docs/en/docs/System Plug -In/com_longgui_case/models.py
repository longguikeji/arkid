from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_case"

class LongguiCaseAppConfig(AppConfig):
    name = app_label
    
class CaseUser(UserExpandAbstract):
    class Meta:
        app_label = app_label
    
    nickname = models.CharField(verbose_name=_('Nickname', '昵称'),blank=True,null=True, max_length=128)