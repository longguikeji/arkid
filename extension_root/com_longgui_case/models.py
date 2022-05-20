from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_case"

class LongguiCaseAppConfig(AppConfig):
    name = app_label
    

# class CaseUser(UserExpandAbstract):
#     class Meta:
#         app_label = "com_longgui_case"
#     nickname = models.CharField(verbose_name=_('nickname', '昵称'), max_length=128)
    
class CaseUser(create_expand_abstract_model(UserExpandAbstract, app_label, 'CaseUser')):
    class Meta:
        app_label = app_label
    
    nickname = models.CharField(verbose_name=_('nickname', '昵称'), max_length=128)