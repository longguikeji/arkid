from django.db import models
from django.utils.translation import ugettext_lazy as _
from app.models import App
from inventory.models import Tenant
from common.model import BaseModel


class ApplicationGroup(BaseModel):
    
    name = models.CharField(
        verbose_name=_("名称"),
        max_length=100
    )

    apps = models.ManyToManyField(
        App,
        verbose_name=_('应用'),
        related_name="application_groups"
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        verbose_name=_("租户")
    )

    class Meta:
        verbose_name = _("应用分组")
        
    def delete(self, *args, **kwargs):
        self.apps.clear()
        return super().delete(*args, **kwargs)
