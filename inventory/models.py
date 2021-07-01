from typing import List
from django.db import models
from django.db.models.fields import related
from tenant.models import Tenant
from common.model import BaseModel
from django.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)
from django.contrib.auth.models import AbstractUser
from common.model import BaseModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import PermissionManager
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from django_scim.models import AbstractSCIMUserMixin, AbstractSCIMGroupMixin


class Permission(BaseModel):

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
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


class User(AbstractSCIMUserMixin, AbstractUser, BaseModel):

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
    def scim_groups(self):
        return self.groups

    def set_scim_id(self, is_new):
        if is_new:
            self.__class__.objects.filter(id=self.id).update(scim_id=self.uuid)
            self.scim_id = str(self.uuid)

    @property
    def avatar_url(self):
        from runtime import get_app_runtime

        r = get_app_runtime()
        return r.storage_provider.resolve(self.avatar)

    @property
    def fullname(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def bind_info(self):
        from extension_root.feishu.models import FeishuUser
        from extension_root.gitee.models import GiteeUser
        from extension_root.github.models import GithubUser
        from extension_root.arkid.models import ArkIDUser
        from extension_root.miniprogram.models import MiniProgramUser

        feishuusers = FeishuUser.valid_objects.filter(user=self).exists()
        giteeusers = GiteeUser.valid_objects.filter(user=self).exists()
        githubusers = GithubUser.valid_objects.filter(user=self).exists()
        arkidusers = ArkIDUser.valid_objects.filter(user=self).exists()
        miniprogramusers = MiniProgramUser.valid_objects.filter(user=self).exists()
        result = ''
        if feishuusers:
            result = '飞书 '
        if giteeusers:
            result = result + 'gitee '
        if githubusers:
            result = result + 'github '
        if arkidusers:
            result = result + 'arkid '
        if miniprogramusers:
            result = result + '微信'
        return result

    @property
    def token(self):
        token, _ = Token.objects.get_or_create(
            user=self,
        )
        return token.key

    def refresh_token(self):
        import datetime
        self.last_login = datetime.datetime.now()
        self.save()
        Token.objects.filter(
            user=self
        ).delete()
        token, _ = Token.objects.get_or_create(
            user=self
        )
        return token

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

    def as_dict(self):
        groups = [g.uuid.hex for g in self.groups.all()]
        return {
            'uuid': self.uuid.hex,
            'is_del': self.is_del,
            'is_active': self.is_active,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'mobile': self.mobile,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'country': self.country,
            'city': self.city,
            'job_title': self.job_title,
            'groups': groups,
        }

    def manage_tenants(self):
        from tenant.models import Tenant
        tenants = Tenant.active_objects.all()
        uuids = []
        for tenant in tenants:
            if tenant.has_admin_perm(self):
                uuids.append(tenant.uuid)
        return uuids


class Group(AbstractSCIMGroupMixin, BaseModel):

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )


    name = models.CharField(max_length=128, blank=False, null=True)
    parent = models.ForeignKey(
        'inventory.Group',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
    )
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
        owned_perms = list(
            self.permissions.filter(
                codename__in=perm_codes,
            )
        )
        if self.parent is not None:
            owned_perms += list(self.parent.owned_perms(perm_codes))

        return owned_perms

    def as_dict(self):
        return {
            'uuid': self.uuid.hex,
            'is_del': self.is_del,
            'is_active': self.is_active,
            'name': self.name,
            'parent': self.parent and self.parent.uuid.hex,
        }

    def set_scim_id(self, is_new):
        if is_new:
            self.__class__.objects.filter(id=self.id).update(scim_id=self.uuid)
            self.scim_id = str(self.uuid)

class CustomField(BaseModel):
    '''
    自定义字段
    '''

    SUBJECT_CHOICES = (
        ('user', '内部联系人'),    # '^[a-z]{1,16}$'
        ('extern_user', '外部联系人'),
        ('node', '组'),
    )

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    name = models.CharField(max_length=128, verbose_name='字段名称')
    subject = models.CharField(choices=SUBJECT_CHOICES, default='user', max_length=128, verbose_name='字段分类')
    schema = models.JSONField(default={'type': 'string'}, verbose_name='字段定义')
    is_visible = models.BooleanField(default=True, verbose_name='是否展示')


class NativeField(BaseModel):
    '''
    原生字段
    '''
    SUBJECT_CHOICES = (
        ('user', '内部联系人'),    # '^[a-z]{1,16}$'
        ('extern_user', '外部联系人'),
    )
    name = models.CharField(max_length=128, verbose_name='字段名称')
    key = models.CharField(max_length=256, verbose_name='内部字段名')
    subject = models.CharField(choices=SUBJECT_CHOICES, default='user', max_length=128, verbose_name='字段分类')
    schema = models.JSONField(default={'type': 'string'}, verbose_name='字段定义')
    is_visible = models.BooleanField(default=True, verbose_name='是否展示')
    is_visible_editable = models.BooleanField(default=True, verbose_name='对于`是否展示`，是否可以修改')


class CustomUser(BaseModel):
    '''
    定制化用户信息
    '''
    DEFAULT_VALUE = ""

    user = models.OneToOneField(User, verbose_name='用户', related_name='custom_user', on_delete=models.CASCADE)
    data = models.JSONField(verbose_name='信息内容')

    def update(self, **kwargs):
        '''
        更新数据
        '''
        self.data.update(**kwargs)    # pylint: disable=no-member
        self.save()

    def pretty(self, visible_only=True):
        '''
        前端友好的输出
        '''
        # pylint: disable=no-member
        res = []
        data = self.data

        kwargs = {}
        if visible_only:
            kwargs.update(is_visible=True)

        for field in CustomField.valid_objects.filter(**kwargs):
            res.append({
                'uuid': field.uuid.hex,
                'name': field.name,
                'value': data.get(field.uuid.hex, ''),
            })
        return res
