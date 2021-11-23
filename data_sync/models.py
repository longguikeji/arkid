from common.model import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class DataSyncConfig(BaseModel):
    SYNC_MODES = (
        ('client', _("Client mode")),
        ('server', _("Server mode")),
    )

    name = models.CharField(
        max_length=128, verbose_name=_('配置名称'), unique=True, default=''
    )
    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    type = models.CharField(max_length=128, verbose_name=_('数据同步类型'))
    data = models.JSONField(default=dict)
    sync_mode = models.CharField(
        max_length=32, choices=SYNC_MODES, verbose_name=_('同步模式'), default='server'
    )

    @property
    def data_sync_extentions(self):
        from runtime import get_app_runtime

        r = get_app_runtime()
        return r.data_sync_extensions
