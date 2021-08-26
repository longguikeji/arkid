#!/usr/bin/env python3


from common.model import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class LoginRegisterConfig(BaseModel):

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    type = models.CharField(max_length=32, verbose_name=_('Login Register Config Type'))
    data = models.JSONField(default=dict)
