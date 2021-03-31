from typing import List
from django.db import models
from django.db.models.fields import related
from tenant.models import Tenant
from common.model import BaseModel
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.contrib.auth.models import AbstractUser
from common.model import BaseModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import PermissionManager
from django.utils.translation import gettext_lazy as _


class Permission(BaseModel):

    tenant = models.ForeignKey('tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT)
    name = models.CharField(_('name'), max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name=_('content type'),
        related_name='upermission_content_type',
    )
    codename = models.CharField(_('codename'), max_length=100)

    objects = PermissionManager()

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        unique_together = [['content_type', 'codename']]
        ordering = ['content_type__app_label', 'content_type__model', 'codename']

    def __str__(self):
        return '%s | %s' % (self.content_type, self.name)

    def natural_key(self):
        return (self.codename,) + self.content_type.natural_key()

    natural_key.dependencies = ['contenttypes.contenttype']


class User(AbstractUser, BaseModel):
    
    tenants = models.ManyToManyField(
        'tenant.Tenant',
        blank=True,
        related_name="user_tenant_set",
        related_query_name="tenant",
    )

    username = models.CharField(max_length=128, blank=False, unique=True)
    password = models.CharField(max_length=128, blank=False, null=True)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=128, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    nickname = models.CharField(max_length=128, blank=True)
    country = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True)
    job_title = models.CharField(max_length=128, blank=True)
    last_login = models.DateTimeField(blank=True, null=True)

    avatar = models.CharField(blank=True, max_length=256)

    groups = models.ManyToManyField(
        'inventory.Group',
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'inventory.Permission',
        blank=True,
        related_name="user_permission_set",
        related_query_name="user_permission",
    )

    _password = None

    @property
    def avatar_url(self):
        from runtime import get_app_runtime
        r = get_app_runtime()
        return r.storage_provider.resolve(self.avatar)

    @property
    def fullname(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)


class Group(BaseModel):

    tenant = models.ForeignKey('tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=128, blank=False, null=True)
    parent = models.ForeignKey('inventory.Group', null=True, blank=True, on_delete=models.PROTECT, related_name='children')
    permissions = models.ManyToManyField(
        'inventory.Permission',
        blank=True,
    )

    def __str__(self) -> str:
        return f'{self.tenant.name} - {self.name}'

    @property
    def children(self):
        return Group.valid_objects.filter(parent=self).order_by('id')

    def owned_perms(self, perm_codes: List):
        owned_perms = list(self.permissions.filter(
            codename__in=perm_codes,
        ))
        if self.parent is not None:
            owned_perms += list(self.parent.owned_perms(perm_codes))

        return owned_perms
