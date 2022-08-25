from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from django.db import models
from arkid.common.model import BaseModel
from arkid.core.models import Tenant, User
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_logging_mysql"

class LonggingMysqlAppConfig(AppConfig):
    name = app_label


class Log(BaseModel):

    class Meta:
        app_label = app_label

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='用户')
    data = models.JSONField(blank=True, default=dict)
