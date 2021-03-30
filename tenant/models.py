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
