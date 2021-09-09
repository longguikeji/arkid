from django.db import models
from common.model import BaseModel
from tenant.models import Tenant
from django.utils.translation import gettext_lazy as _
import string
from urllib.parse import quote


class App(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    _url = models.CharField(max_length=1024, blank=True, db_column="url")
    logo = models.FileField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=128, verbose_name=_('App Type'))
    data = models.JSONField(blank=True, default=dict)
    auth_tmpl = models.TextField(blank=True, null=True, default='')

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

    def get_url(self):
        from runtime import get_app_runtime
        if getattr(get_app_runtime(), "auth_rule_types", None):
            return f"/api/v1/tenant/{self.tenant.uuid}/auth_rule/app_login_hook/?app_id={self.id}"
        else:
            return self._url

    def set_url(self, val):
        self.url = val

    url = property(get_url, set_url)

    def as_dict(self):
        return {
            'uuid': self.uuid.hex,
            'is_del': self.is_del,
            'is_active': self.is_active,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'type': self.type,
            'data': self.data,
        }


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
