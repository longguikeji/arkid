#!/usr/bin/env python3
from django.db import models
from tenant.models import Tenant
from common.model import BaseModel


class PrivacyNotice(BaseModel):

    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        verbose_name='租户',
        related_name='privacy_notice',
        null=True,
        blank=True,
    )
    title = models.CharField(
        verbose_name='标题', max_length=128, blank=True, null=True, default=''
    )
    content = models.TextField(verbose_name='内容', blank=True, null=True, default='')

    def __str__(self) -> str:
        return f'Privacy Notice: {self.title}'


class PasswordComplexity(BaseModel):

    tenant = models.ForeignKey(
        Tenant, on_delete=models.PROTECT, verbose_name='租户', null=True, blank=True
    )
    regular = models.CharField(verbose_name='正则表达式', max_length=512)
    is_apply = models.BooleanField(default=False, verbose_name='是否启用')
    title = models.CharField(
        verbose_name='标题', max_length=128, default='', null=True, blank=True
    )

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

class PlatformConfig(BaseModel):

    frontend_url = models.URLField(
        verbose_name='ArkId访问地址', max_length=128, blank=True, null=True, default=''
    )