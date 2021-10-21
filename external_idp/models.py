from common.model import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExternalIdp(BaseModel):

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    type = models.CharField(max_length=128, verbose_name=_('External IDP Type'))
    data = models.JSONField(default=dict)
    order_no = models.PositiveSmallIntegerField(default=0)

    @property
    def external_idp_types(self):
        from runtime import get_app_runtime

        r = get_app_runtime()
        return r.external_idps
