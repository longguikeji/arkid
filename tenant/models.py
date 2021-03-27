from django.db import models
from common.model import BaseModel


class Tenant(BaseModel):

    name = models.CharField(verbose_name='名字', max_length=128)
    slug = models.SlugField(verbose_name='短链接标识')
    icon = models.URLField(verbose_name='图标',blank=True)

    def __str__(self) -> str:
        return f'Tenant: {self.name}'