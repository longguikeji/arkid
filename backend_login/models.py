from common.model import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class BackendLogin(BaseModel):

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    type = models.CharField(max_length=128, verbose_name=_('Backend Login Type'))
    data = models.JSONField(default=dict)
    order_no = models.PositiveSmallIntegerField(default=0)
