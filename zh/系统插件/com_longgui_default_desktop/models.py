from email.policy import default
from django.db import models
from arkid.common.model import BaseModel
from arkid.core.translation import gettext_default as _
from arkid.core.models import Tenant
from django.apps import AppConfig

app_label = "com_longgui_default_desktop"

class LongguiDefaultDesktopAppConfig(AppConfig):
    name = app_label
    
class DefaultDesktop(BaseModel):
    class Meta:
        app_label = app_label
    
    default_desktop = models.CharField(verbose_name=_('Default Desktop', '默认桌面'),blank=True,null=True, max_length=1024,default="/desktop/")
    
    target = models.OneToOneField(
        Tenant,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s",
    )
