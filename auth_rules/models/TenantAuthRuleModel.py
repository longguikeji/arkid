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

    @property
    def provider(self):
        from runtime import get_app_runtime
        return get_app_runtime().auth_rule_type_providers.get(self.type)()

    def save(self,*args, **kwargs) -> None:
        from runtime import get_app_runtime
        get_app_runtime().auth_rules.append(self)
        return super().save(*args, **kwargs)
