"""
认证规则
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from common.model import BaseModel
from inventory.models import Tenant


class TenantAuthRule(BaseModel):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        verbose_name=_('租户')
    )

    is_apply = models.BooleanField(
        default=False,
        verbose_name=_('是否启用')
    )

    title = models.CharField(
        verbose_name=_('标题'),
        max_length=128,
        default='',
        null=True,
        blank=True
    )
    
    data = models.JSONField(
        blank=True,
        default=dict,
        verbose_name=_("配置数据")
    )

    type = models.CharField(
        verbose_name=_("类型"),
        max_length=100
    )

    @property
    def tenant_uuid(self):
        return self.tenant.uuid
