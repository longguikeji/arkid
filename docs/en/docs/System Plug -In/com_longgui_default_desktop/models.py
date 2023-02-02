from email.policy import default
from django.db import models
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.core.models import TenantExpandAbstract

app_label = "com_longgui_default_desktop"

class LongguiDefaultDesktopAppConfig(AppConfig):
    name = app_label
    
class DefaultDesktop(TenantExpandAbstract):
    class Meta:
        app_label = app_label
    
    default_desktop = models.CharField(verbose_name=_('Default Desktop', '默认桌面'),blank=True,null=True, max_length=1024,default="/desktop/")
    

