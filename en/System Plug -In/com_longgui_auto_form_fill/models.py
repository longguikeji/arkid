from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from django.db import models
from arkid.common.model import BaseModel
from arkid.core.models import Tenant, User, App

app_label = "com_longgui_auto_form_fill"

class LongguiAutoFormFillAppConfig(AppConfig):
    name = app_label
    
class AutoFormFillUser(BaseModel):

    class Meta:
        app_label = app_label

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name='用户')
    tenant = models.ForeignKey(Tenant, blank=True, null=True, on_delete=models.CASCADE, verbose_name='租户')
    app = models.ForeignKey(App, blank=True, null=True, on_delete=models.CASCADE, verbose_name='应用')
    username = models.CharField(verbose_name=_('username', '用户名'), default='', blank=True,null=True, max_length=256)
    password = models.CharField(verbose_name=_('password', '密码'), default='', blank=True,null=True, max_length=256)