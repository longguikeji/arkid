from django.db import models
from common.model import BaseModel
from tenant.models import Tenant
from django.utils.translation import gettext_lazy as _


class App(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024, blank=True)
    logo = models.FileField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=128, verbose_name=_('App Type'))
    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}, App: {self.name}'

    @property
    def app_type(self):
        from runtime import get_app_runtime
        r = get_app_runtime()
        return r.app_types

    @property
    def access_perm_code(self):
        return f'app_access_{self.uuid}'


# class AuthServer(BaseModel):

#     TYPE_CHOICES = (
#         (0, 'Unknown'),
#         (1, 'OAuth 2.0'),
#         (2, 'LDAP'),
#         (3, 'OIDC'),
#         (4, 'SAML'),
#         (5, 'CAS WEB'),
#         (6, 'SWA'),
#         (7, 'WS-Fed'),
#     )

#     # tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
#     app = models.ForeignKey(App, on_delete=models.PROTECT)
#     type = models.IntegerField(choices=TYPE_CHOICES, default=0)
