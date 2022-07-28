import datetime
from django.db import models
from django.utils import timezone
from arkid.common.model import BaseModel
from arkid.common.utils import generate_secret
from arkid.core.translation import gettext_default as _
from arkid.core.expand import ExpandManager, ExpandModel
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.token import generate_token
from typing import List

class EmptyModel(models.Model):
    pass

class Platform(BaseModel, ExpandModel):
    is_saas = models.BooleanField(default=False, verbose_name=_('SaaS Switch', '多租户开关'))
    is_need_rent = models.BooleanField(default=False, verbose_name=_('Is Tenant Need Rent Extension', '租户是否需要租赁插件'))
    
    @classmethod
    def get_config(cls):
        config = Platform.objects.first()
        if not config:
            config = Platform.objects.create()
        return config

class Tenant(BaseModel, ExpandModel):
    class Meta(object):
        verbose_name = _("tenant", "租户")
        verbose_name_plural = _("tenant", "租户")

    name = models.CharField(verbose_name=_('Name', '名字'), max_length=128)
    slug = models.SlugField(verbose_name=_('Slug', '短链接标识'), unique=True, blank=True, null=True)
    icon = models.URLField(verbose_name=_('Icon', '图标'), blank=True, null=True)

    token_duration_minutes = models.IntegerField(
        blank=False,
        default=24 * 60,
        verbose_name=_('Token Duration Minutes', 'Token有效时长(分钟)'),
    )

    users = models.ManyToManyField(
        'User',
        blank=True,
        related_name="tenant_user_set",
        related_query_name="user",
    )

    def __str__(self) -> str:
        return f'Tenant: {self.name}'

    @property
    def admin_perm_code(self):
        return f'tenant_admin_{self.id}'

    def has_admin_perm(self, user: 'User'):
        from arkid.core.perm.permission_data import PermissionData

        permissiondata = PermissionData()
        result = permissiondata.has_admin_perm(self, user)
        return result

    def create_tenant_user_admin_permission(self, user):
        # 此处无法使用celery和event, event会出现无法回调，celery启动时如果调用，会自己调用自己
        from arkid.core.perm.permission_data import PermissionData

        permissiondata = PermissionData()
        permissiondata.create_tenant_user_admin_permission(self, user)

    @property
    def is_platform_tenant(self):
        '''
        是否是平台租户
        '''
        tenant = Tenant.valid_objects.filter(slug='').first()
        if tenant.id == self.id:
            return True
        else:
            return False

    @staticmethod
    def platform_tenant():
        return Tenant.valid_objects.filter(slug='').first()

class User(BaseModel, ExpandModel):
    
    key_fields = {'username':'用户名'}
    
    class Meta(object):
        verbose_name = _("user", "用户")
        verbose_name_plural = _("user", "用户")
        unique_together = [['username', 'tenant']]

    username = models.CharField(max_length=128, blank=False, verbose_name=_("Username","用户名"))
    avatar = models.URLField(verbose_name=_('Avatar', '头像'), blank=True, null=True)
    is_platform_user = models.BooleanField(
        default=False, verbose_name=_('Is Platform User', '是否是平台用户')
    )

    tenant = models.ForeignKey('Tenant', blank=False, on_delete=models.PROTECT)
    scim_external_id = models.CharField(max_length=128, blank=True, null=True)

    # tenants = models.ManyToManyField(
    #     'Tenant',
    #     blank=False,
    #     related_name="user_tenant_set",
    #     related_query_name="tenant",
    # )
    @classmethod
    def register_key_field(cls, **fields):
        for key, value in fields:
            User.key_fields[key] = value

    @property
    def is_superuser(self):
        return (
            True
            if self.id == User.valid_objects.order_by('created').first().id
            else False
        )


class UserGroup(BaseModel, ExpandModel):
    class Meta(object):
        verbose_name = _("User Group", "用户分组")
        verbose_name_plural = _("User Group", "用户分组")

    tenant = models.ForeignKey('Tenant', blank=False, on_delete=models.PROTECT)
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
        verbose_name=_('User List', '用户列表'),
    )
    permission = models.ForeignKey(
        'SystemPermission',
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT,
    )

    scim_external_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def children(self):
        return UserGroup.valid_objects.filter(parent=self).order_by('id')


class App(BaseModel, ExpandModel):
    class Meta(object):
        verbose_name = _("APP", "应用")
        verbose_name_plural = _("APP", "应用")

    tenant = models.ForeignKey('Tenant', blank=False, on_delete=models.PROTECT)
    name = models.CharField(max_length=128, verbose_name=_('name', '名称'))
    url = models.CharField(max_length=1024,null=True,blank=True, verbose_name=_('url', '地址'))
    logo = models.CharField(
        max_length=1024, blank=True, null=True, default='', verbose_name=_('logo', '图标')
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_('description', '描述')
    )
    type = models.CharField(max_length=128, default='', verbose_name=_('type', '类型'))
    secret = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default='',
        verbose_name=_('secret', '密钥'),
    )
    config = models.OneToOneField(
        TenantExtensionConfig,
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT,
    )
    package = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        default='',
        verbose_name=_('package', '包名'),
    )
    entry_permission = models.ForeignKey(
        'SystemPermission',
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT
    )
    arkstore_app_id = models.CharField(
        max_length=1024, blank=True, null=True, default=None, verbose_name=_('Arkstore app id', '方舟商店应用标识')
    )

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}, App: {self.name}'

    def save(self, *args, **kwargs):
        if self.secret == '':
            self.secret = generate_secret()
        super().save(*args, **kwargs)


class AppGroup(BaseModel, ExpandModel):
    class Meta(object):
        verbose_name = _("APP Group", "应用分组")
        verbose_name_plural = _("APP Group", "应用分组")

    tenant = models.ForeignKey('Tenant', blank=False, on_delete=models.PROTECT)
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
        verbose_name=_('APP List', '应用列表'),
    )

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def children(self):
        return AppGroup.valid_objects.filter(parent=self).order_by('id')


class PermissionAbstract(BaseModel, ExpandModel):
    class Meta(object):
        abstract = True

    CATEGORY_CHOICES = (
        ('entry', _('entry', '入口')),
        ('api', _('API', '接口')),
        ('data', _('data', '数据')),
        ('group', _('group', '分组')),
        ('ui', _('UI', '界面')),
        ('other', _('other', '其它')),
    )

    name = models.CharField(verbose_name=_('Name', '名称'), max_length=255)
    code = models.CharField(verbose_name=_('Code', '编码'), max_length=100)
    tenant = models.ForeignKey(
        'Tenant',
        default=None,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('Tenant', '租户'),
    )

    category = models.CharField(
        choices=CATEGORY_CHOICES,
        default="other",
        max_length=100,
        verbose_name=_('category', "类型"),
    )
    is_system = models.BooleanField(
        default=True, verbose_name=_('System Permission', '是否是系统权限')
    )
    operation_id = models.CharField(
        verbose_name=_('Operation ID', '操作id'),
        max_length=255,
        blank=True,
        null=True,
        default='',
    )
    describe = models.JSONField(
        blank=True, default=dict, verbose_name=_('describe', '描述')
    )
    is_update = models.BooleanField(default=False, verbose_name='是否更新')
    is_open = models.BooleanField(
        default=False, verbose_name=_('is open', '是否开放给其它租户访问'),
    )

    def __str__(self):
        return '%s' % (self.name)


class SystemPermission(PermissionAbstract):
    class Meta(object):
        verbose_name = _('SystemPermission', '系统权限')
        verbose_name_plural = _('SystemPermission', '系统权限')

    # django 只允许有一个主键，一个自增
    sort_id = models.IntegerField(verbose_name=_('Sort ID', '序号'), default=-1)

    container = models.ManyToManyField(
        'SystemPermission',
        blank=True,
        related_name="system_permission_set",
        related_query_name="system_permission",
        verbose_name=_('SystemPermission List', '包含的系统权限'),
    )
    parent = models.ForeignKey(
        'SystemPermission',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
        verbose_name=_('Parent', '父权限分组'),
    )

    def save(self, *args, **kwargs):
        if self.sort_id == -1:
            self.sort_id = SystemPermission.objects.count()
        super().save(*args, **kwargs)

    @property
    def children(self):
        return SystemPermission.valid_objects.filter(parent=self).order_by('id')


class Permission(PermissionAbstract):
    class Meta(object):
        verbose_name = _("Permission", "权限")
        verbose_name_plural = _("Permission", "权限")

    # def anto_sort():
    #     # 方法必须放在字段前面(有bug不同应用之间会互相占用)
    #     count=Permission.objects.count()
    #     return 0 if (count == 0) else count

    sort_id = models.IntegerField(verbose_name=_('Sort ID', '序号'), default=-1)

    app = models.ForeignKey(
        App,
        models.PROTECT,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('APP', '应用'),
    )
    parent = models.ForeignKey(
        'Permission',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
        verbose_name=_('Parent', '父权限分组'),
    )
    container = models.ManyToManyField(
        'Permission',
        blank=True,
        related_name="permission_set",
        related_query_name="permission",
        verbose_name=_('Permission List', '权限列表'),
    )

    def __str__(self) -> str:
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if self.sort_id == -1:
            permission = (
                Permission.objects.filter(tenant=self.tenant, app_id=self.app_id)
                .order_by('-sort_id')
                .first()
            )
            if permission:
                self.sort_id = permission.sort_id + 1
            else:
                self.sort_id = 0
        super().save(*args, **kwargs)

    @property
    def children(self):
        return Permission.valid_objects.filter(parent=self).order_by('id')


class UserPermissionResult(BaseModel, ExpandModel):
    class Meta(object):
        verbose_name = _("UserPermissionResult", "用户权限结果")
        verbose_name_plural = _("UserPermissionResult", "用户权限结果")

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    app = models.ForeignKey(
        App,
        default=None,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name='App',
    )
    result = models.CharField(
        max_length=1024, blank=True, null=True, verbose_name='权限结果'
    )

    def __str__(self) -> str:
        return f'User: {self.user.username}'


class GroupPermissionResult(BaseModel, ExpandModel):
    class Meta(object):
        verbose_name = _("GroupPermissionResult", "分组权限结果")
        verbose_name_plural = _("GroupPermissionResult", "分组权限结果")

    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, verbose_name='用户分组')
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    app = models.ForeignKey(
        App,
        default=None,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name='App',
    )
    result = models.CharField(
        max_length=1024, blank=True, null=True, verbose_name='权限结果'
    )

    def __str__(self) -> str:
        return f'User: {self.user_group.name}'


# class Approve(BaseModel, ExpandModel):
#     class Meta(object):
#         verbose_name = _('Approve', "审批动作")
#         verbose_name_plural = _('Approve', "审批动作")

#     STATUS_CHOICES = (
#         ('wait', _('Wait', '待审批')),
#         ('pass', _('Pass', '通过')),
#         ('deny', _('Deny', '拒绝')),
#     )

#     name = models.CharField(verbose_name=_('Name', '名称'), max_length=255)
#     code = models.CharField(verbose_name=_('Code', '编码'), max_length=100)
#     description = models.TextField(
#         blank=True, null=True, verbose_name=_('Description', '备注')
#     )
#     tenant = models.ForeignKey(
#         'Tenant', default=None, on_delete=models.PROTECT, verbose_name=_('Tenant', '租户')
#     )
#     app = models.ForeignKey(
#         App,
#         models.PROTECT,
#         default=None,
#         null=True,
#         blank=True,
#         verbose_name=_('APP', '应用'),
#     )
#     status = models.CharField(
#         choices=STATUS_CHOICES,
#         default="wait",
#         max_length=100,
#         verbose_name=_('Status', "状态"),
#     )
#     data = models.JSONField(
#         default=dict,
#         verbose_name=_('Data', "数据"),
#     )

#     def __str__(self):
#         return '%s' % (self.name)


class ExpiringToken(models.Model):
    class Meta(object):
        verbose_name = _("Token", "秘钥")
        verbose_name_plural = _("Token", "秘钥")

    user = models.OneToOneField(
        'User',
        related_name='auth_token',
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name=_("User", '用户'),
    )
    token = models.CharField(
        _("Token", '秘钥'),
        max_length=40,
        unique=True,
        db_index=True,
        default=generate_token,
    )
    created = models.DateTimeField(_("Created", '创建时间'), auto_now=True)

    def expired(self, tenant):
        """Return boolean indicating token expiration."""
        now = timezone.now()
        token_duration_minutes = tenant.token_duration_minutes
        if self.created < now - datetime.timedelta(minutes=token_duration_minutes):
            return True
        return False

    def __str__(self):
        return self.token


class ApproveAction(BaseModel, ExpandModel):
    class Meta(object):
        verbose_name = _('Approve Action', "审批动作")
        verbose_name_plural = _('Approve Action', "审批动作")

    name = models.CharField(verbose_name=_('Name', '名称'), max_length=255)
    path = models.CharField(verbose_name=_('Request Path', '请求路径'), max_length=100)
    method = models.CharField(verbose_name=_('Request Method', '请求方法'), max_length=50)
    description = models.TextField(
        blank=True, null=True, verbose_name=_('Description', '备注')
    )
    extension = models.ForeignKey(
        Extension,
        default=None,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Extension', '插件'),
        related_name="approve_action_set",
        related_query_name="actions",
    )
    tenant = models.ForeignKey(
        'Tenant',
        default=None,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_('Tenant', '租户'),
        related_name="approve_action_set",
        related_query_name="actions",
    )

    def __str__(self):
        return '%s' % (self.name)


class ApproveRequest(BaseModel, ExpandModel):

    STATUS_CHOICES = (
        ('wait', _('Wait', '待审批')),
        ('pass', _('Pass', '通过')),
        ('deny', _('Deny', '拒绝')),
    )

    class Meta(object):
        verbose_name = _('Approve Request', "审批请求")
        verbose_name_plural = _('Approve Request', "审批请求")

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name=_('User', '用户'),
        related_name="approve_request_set",
        related_query_name="requests",
    )

    action = models.ForeignKey(
        'ApproveAction',
        default=None,
        on_delete=models.CASCADE,
        verbose_name=_('Request Action', '审批动作'),
        related_name="approve_request_set",
        related_query_name="requests",
    )
    # path = models.CharField(verbose_name=_('Request Path','请求路径'), max_length=100)
    # method = models.CharField(verbose_name=_('Request Method','请求方法'), max_length=50)
    environ = models.JSONField(verbose_name=_('Request Environ', '请求环境变量'))
    body = models.BinaryField(verbose_name=_('Request Body', '请求负载'))

    status = models.CharField(
        choices=STATUS_CHOICES,
        default="wait",
        max_length=100,
        verbose_name=_('Status', "状态"),
    )

    def __str__(self):
        return (
            f'{self.action.name}:{self.action.method}:{self.action.path}:{self.status}'
        )


class LanguageData(BaseModel):
    class Meta(object):
        verbose_name = _('Language Data', "语言包数据")
        verbose_name_plural = _('Language Data', "语言包数据")

    name = models.CharField(verbose_name=_('Name', '名称'), max_length=255)

    extension = models.OneToOneField(
        Extension,
        default=None,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_('Extension', '插件'),
        related_name="language_data",
        related_query_name="language_data",
    )

    extension_data = models.JSONField(verbose_name=_("插件自带数据"), blank=True, null=True)

    custom_data = models.JSONField(verbose_name=_(""), blank=True, null=True)

    @property
    def count(self):
        extension_data_count = len(self.extension_data) if self.extension_data else 0
        custom_data_count = len(self.custom_data) if self.custom_data else 0
        return extension_data_count + custom_data_count

    @property
    def data(self):
        data = self.extension_data or {}
        if self.custom_data:
            data.update(self.custom_data)
        return data


class AccountLifeCrontab(BaseModel):
    class Meta(object):
        verbose_name = _("Account Life Crontab", "生命周期定时任务配置")
        verbose_name_plural = _("Account Life Crontab", "生命周期定时任务配置")

    name = models.CharField(
        blank=True,
        null=True,
        default='',
        verbose_name=_('name', '名字'),
        max_length=128,
    )
    tenant = models.ForeignKey(
        'Tenant',
        default=None,
        on_delete=models.CASCADE,
        verbose_name=_('Tenant', '租户'),
    )
    config = models.JSONField(
        null=True, blank=True, default=dict, verbose_name=_('Config', '定时任务配置')
    )


class TenantExpandAbstract(BaseModel):
    class Meta:
        abstract = True

    foreign_key = Tenant
    
    target = models.OneToOneField(
        Tenant,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s",
    )


class UserExpandAbstract(BaseModel):
    class Meta:
        abstract = True
    foreign_key = User
        
    target = models.OneToOneField(
        User,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s",
    )


class UserGroupExpandAbstract(BaseModel):
    class Meta:
        abstract = True

    foreign_key = UserGroup
    
    target = models.OneToOneField(
        UserGroup,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s",
    )


class AppExpandAbstract(BaseModel):
    class Meta:
        abstract = True

    foreign_key = App
    target = models.OneToOneField(
        App,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s",
    )


class AppGroupExpandAbstract(BaseModel):
    class Meta:
        abstract = True
        
    foreign_key = AppGroup
    target = models.OneToOneField(
        AppGroup,
        blank=True,
        default=None,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s",
    )
