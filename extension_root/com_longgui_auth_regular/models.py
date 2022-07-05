from arkid.core.models import Tenant
from arkid.common.model import BaseModel
from arkid.core.translation import gettext_default as _

app_label = 'com_longgui_auth_regular'

class AuthRule(BaseModel):

    class Meta:
        app_label = app_label

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    app = models.ForeignKey(
        App,
        default=None,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name='应用',
    )
    result = models.CharField(
        max_length=1024, blank=True, null=True, verbose_name='权限结果'
    )
    is_own = models.BooleanField(default=True, verbose_name='是否拥有')

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}'
