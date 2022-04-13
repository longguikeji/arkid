import os
import binascii
import datetime
from django.db import models
from django.utils import timezone
from arkid.common.model import BaseModel
from arkid.core.translation import gettext_default as _
# from oauth2_provider.generators import generate_client_secret
from arkid.core.expand import ExpandManager, ExpandModel


class Tenant(BaseModel):

    class Meta(object):
        verbose_name = _("tenant", "租户")
        verbose_name_plural = _("tenant", "租户")

    name = models.CharField(verbose_name=_('name', '名字'), max_length=128)
    slug = models.SlugField(verbose_name=_('slug', '短链接标识'), unique=True)
    icon = models.URLField(verbose_name=_('icon', '图标'), blank=True)

    def __str__(self) -> str:
        return f'Tenant: {self.name}'


class User(ExpandModel, BaseModel):
    
    class Meta(object):
        verbose_name = _("user", "用户")
        verbose_name_plural = _("user", "用户")

    username = models.CharField(max_length=128, blank=False)
    avatar = models.URLField(verbose_name=_('Avatar','头像'), blank=True)
    is_platform_user = models.BooleanField(default=False, verbose_name=_('is platform user','是否是平台用户'))

    tenants = models.ManyToManyField(
        'Tenant',
        blank=False,
        related_name="user_tenant_set",
        related_query_name="tenant",
    )


class UserGroup(ExpandModel, BaseModel):

    class Meta(object):
        verbose_name = _("User Group","用户分组")
        verbose_name_plural = _("User Group","用户分组")

    tenant = models.ForeignKey(
        'Tenant', blank=False, on_delete=models.PROTECT
    )
    name = models.CharField(max_length=128, blank=False)
    parent = models.ForeignKey(
        'UserGroup',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
    )
    users = models.ManyToManyField(
        'User',
        blank=True,
        related_name="user_set",
        related_query_name="user",
        verbose_name=_('User List','用户列表')
    )

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def children(self):
        return UserGroup.valid_objects.filter(parent=self).order_by('id')


class App(ExpandModel, BaseModel):

    class Meta(object):
        verbose_name = _("APP","应用")
        verbose_name_plural = _("APP", "应用")

    tenant = models.ForeignKey(
        'Tenant', blank=False, on_delete=models.PROTECT
    )
    name = models.CharField(max_length=128, verbose_name=_('name','名称'))
    url = models.CharField(max_length=1024, blank=True, verbose_name=_('url','地址'))
    logo = models.CharField(max_length=1024, blank=True, null=True, default='', verbose_name=_('logo','图标'))
    description = models.TextField(blank=True, null=True, verbose_name=_('description','描述'))
    type = models.CharField(max_length=128, verbose_name=_('type','类型'))
    data = models.JSONField(blank=True, default=dict, verbose_name=_('data','配置'))
    secret = models.CharField(
        max_length=255, blank=True, null=True, default='', verbose_name=_('secret','密钥')
    )

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}, App: {self.name}'


class AppGroup(ExpandModel, BaseModel):

    class Meta(object):
        verbose_name = _("APP Group","应用分组")
        verbose_name_plural = _("APP Group","应用分组")

    tenant = models.ForeignKey(
        'Tenant', blank=False, on_delete=models.PROTECT
    )
    name = models.CharField(max_length=128, blank=False)
    parent = models.ForeignKey(
        'AppGroup',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
    )
    apps = models.ManyToManyField(
        App,
        blank=True,
        related_name="app_set",
        related_query_name="app",
        verbose_name=_('APP List', '应用列表')
    )

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def children(self):
        return AppGroup.valid_objects.filter(parent=self).order_by('id')


class PermissionAbstract(ExpandModel, BaseModel):

    class Meta(object):
        abstract = True

    CATEGORY_CHOICES = (
        ('entry', _('entry','入口')),
        ('api', _('API','接口')),
        ('data', _('data','数据')),
        ('group', _('group','分组')),
        ('ui', _('UI','界面')),
        ('other', _('other','其它')),
    )

    name = models.CharField(verbose_name=_('Name','名称'), max_length=255)
    code = models.CharField(verbose_name=_('Code','编码'), max_length=100)
    tenant = models.ForeignKey(
        'Tenant', default=None, on_delete=models.PROTECT, verbose_name=_('Tenant','租户')
    )
    app = models.ForeignKey(
        App,
        models.PROTECT,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('APP','应用')
    )
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        default="other",
        max_length=100,
        verbose_name=_('category',"类型"),
    )
    is_system = models.BooleanField(
        default=True,
        verbose_name=_('System Permission','是否是系统权限')
    )

    def __str__(self):
        return '%s' % (self.name)


class Permission(PermissionAbstract):

    class Meta(object):
        verbose_name = _("Permission", "权限")
        verbose_name_plural = _("Permission", "权限")

    parent = models.ForeignKey(
        'Permission',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
        verbose_name=_('Parent', '父权限分组')
    )
    permissions = models.ManyToManyField(
        'Permission',
        blank=True,
        related_name="permission_set",
        related_query_name="permission",
        verbose_name=_('Permission List','权限列表')
    )

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def children(self):
        return Permission.valid_objects.filter(parent=self).order_by('id')


class Approve(ExpandModel, BaseModel):

    class Meta(object):
        verbose_name = _('Approve',"审批动作")
        verbose_name_plural = _('Approve',"审批动作")

    STATUS_CHOICES = (
        ('wait', _('Wait','待审批')),
        ('pass', _('Pass','通过')),
        ('deny', _('Deny','拒绝')),
    )

    name = models.CharField(verbose_name=_('Name','名称'), max_length=255)
    code = models.CharField(verbose_name=_('Code','编码'), max_length=100)
    description = models.TextField(blank=True, null=True, verbose_name=_('Description','备注'))
    tenant = models.ForeignKey(
        'Tenant', default=None, on_delete=models.PROTECT, verbose_name=_('Tenant','租户')
    )
    app = models.ForeignKey(
        App,
        models.PROTECT,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('APP','应用')
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        default="wait",
        max_length=100,
        verbose_name=_('Status',"状态"),
    )
    data = models.JSONField(
        default=dict,
        verbose_name=_('Data',"数据"),
    )

    def __str__(self):
        return '%s' % (self.name)


class ExpiringToken(models.Model):

    class Meta(object):
        verbose_name = _("Token","秘钥")
        verbose_name_plural = _("Token","秘钥")

    user = models.OneToOneField(
        'User', related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User",'用户')
    )
    token = models.CharField(_("Token",'秘钥'), max_length=40, primary_key=True)
    created = models.DateTimeField(_("Created",'创建时间'), auto_now_add=True)
    
    def expired(self, tenant):
        """Return boolean indicating token expiration."""
        now = timezone.now()
        config = TenantConfig.active_objects.filter(tenant=tenant).first()
        if config:
            token_duration_minutes = config.token_duration_minutes
        else:
            token_duration_minutes = 24*60
        if self.created < now - datetime.timedelta(minutes=token_duration_minutes):
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_token(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    @classmethod
    def refresh_token(self):
        self.token = self.generate_token()
        self.save()

    def __str__(self):
        return self.token


class TenantConfig(ExpandModel, BaseModel):

    class Meta(object):
        verbose_name = _('Tenant Config',"租户配置")
        verbose_name_plural = _('Tenant Config',"租户配置")

    tenant = models.ForeignKey('Tenant', blank=False, on_delete=models.PROTECT, verbose_name=_('Tenant','租户'))
    token_duration_minutes = models.IntegerField(blank=False, default=24*60, verbose_name=_('Token Duration Minutes','Token有效时长(分钟)'))
