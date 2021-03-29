from typing import Optional, Callable

from django.db import models
from common.model import BaseModel
from django.utils.translation import gettext_lazy as _


class Extension(BaseModel):

    tenant = models.ForeignKey('tenant.Tenant', blank=True, null=True, on_delete=models.PROTECT, verbose_name=_('Tenant'))
    type = models.CharField(max_length=128, verbose_name=_('Extension Type'))
    data = models.JSONField(blank=True, default=dict, verbose_name=_('Settings'))

    def __str__(self) -> str:
        return self.type

    @property
    def inmem(self):
        from extension.utils import find_installed_extensions
        for ext in find_installed_extensions():
            if ext.name == self.name:
                return ext

        return None
