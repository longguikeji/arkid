from django.db import models
from common.model import BaseModel
from tenant.models import Tenant


class TenantUserConfig(BaseModel):

    class Meta:

        app_label = 'tenantuserconfig'

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}'
