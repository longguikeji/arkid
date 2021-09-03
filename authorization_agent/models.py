from common.model import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuthorizationAgent(BaseModel):

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    type = models.CharField(max_length=128, verbose_name=_('身份源类型类型'))
    data = models.JSONField(default=dict)
    order_no = models.PositiveSmallIntegerField(default=0,verbose_name=_("序号"))

    @property
    def authorization_agent_types(self):
        from runtime import get_app_runtime

        r = get_app_runtime()
        return r.authorization_agents