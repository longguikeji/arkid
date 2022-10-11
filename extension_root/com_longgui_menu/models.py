from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.common.model import BaseModel
from django.apps import AppConfig

app_label = "com_longgui_menu"

class LongguiMenuConfig(AppConfig):
    name = app_label
    
class Menu(BaseModel):

    class Meta:
        app_label = app_label
    
    path = models.CharField(verbose_name=_('path', '路径'), default='', blank=True,null=True, max_length=256)
    name = models.CharField(verbose_name=_('name', '名称'), default='', blank=True,null=True, max_length=256)