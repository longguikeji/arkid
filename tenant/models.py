from django.db import models
from common.model import BaseModel
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from inventory.models import User


class Tenant(BaseModel):

    name = models.CharField(verbose_name='名字', max_length=128)
    slug = models.SlugField(verbose_name='短链接标识')
    icon = models.URLField(verbose_name='图标', blank=True)

    def __str__(self) -> str:
        return f'Tenant: {self.name}'

    @property
    def admin_perm_code(self):
        return f'tenant_admin_{self.uuid}'

    def has_admin_perm(self, user: 'User'):
        return user.is_superuser or user.user_permissions.filter(codename=self.admin_perm_code).count() > 0
    
    @property
    def password_complexity(self):
        result = {}
        comlexity = TenantPasswordComplexity.active_objects.filter(tenant=self, is_apply=True).first()
        if comlexity:
            result['title'] = comlexity.title
            result['regular']= comlexity.regular
        return result


class TenantConfig(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}'

    @property
    def tenant_uuid(self):
        return self.tenant.uuid


class TenantPasswordComplexity(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    regular = models.CharField(verbose_name='正则表达式', max_length=512)
    is_apply = models.BooleanField(default=False, verbose_name='是否启用')
    title = models.CharField(verbose_name='标题', max_length=128, default='')

    @property
    def tenant_uuid(self):
        return self.tenant.uuid
    
    def check_pwd(self, pwd):
        import re
        result = re.match(self.regular, pwd)
        if result:
            return True
        else:
            return False