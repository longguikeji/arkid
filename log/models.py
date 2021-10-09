from django.db import models
from common.model import BaseModel
from tenant.models import Tenant


class Log(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}'
