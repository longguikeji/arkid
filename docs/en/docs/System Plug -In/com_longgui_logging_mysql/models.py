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

    tenant = models.ForeignKey(Tenant, blank=True, null=True, on_delete=models.CASCADE, verbose_name='租户')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name='用户')
    is_tenant_admin = models.BooleanField(blank=True, default=False, verbose_name='是否管理员日志')
    data = models.JSONField(blank=True, default=dict, verbose_name='日志数据')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='创建时间', db_index = True)
    username = models.CharField(max_length=128, blank=False, null=True, db_index = True)
    request_path = models.CharField(max_length=760, blank=False, null=True, db_index = True)
    status_code = models.IntegerField(blank=False, null=True, db_index = True)


class TenantLogConfig(BaseModel):

    class Meta:
        app_label = app_label

    tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    log_retention_period = models.IntegerField(blank=True, default=30, verbose_name='日志保存天数')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_index=True, verbose_name='创建时间')
