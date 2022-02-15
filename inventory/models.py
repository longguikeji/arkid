import base64
import json
import datetime
from cryptography.fernet import Fernet, InvalidToken
from django.utils import timezone
from django.conf import settings
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
from app.models import App
from common.model import BaseModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import PermissionManager
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from django_scim.models import AbstractSCIMUserMixin, AbstractSCIMGroupMixin

KEY = Fernet(base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32]))


class Permission(BaseModel):

    # TYPE_CHOICES = (
    #     (0, '入口'),
    #     (1, 'API'),
    #     (2, '数据'),
    # )

    # django 自带权限字段
    name = models.CharField(_('name'), max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name=_('content type'),
        related_name='upermission_content_type',
    )
    codename = models.CharField(_('codename'), max_length=100)
    # 用户扩展的权限字段
    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    app = models.ForeignKey(
        App,
        models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )
    permission_category = models.CharField(_('权限类型'), blank=False, null=True, default='', max_length=64)
    is_system_permission = models.BooleanField(
        default=True,
        verbose_name='是否是系统权限'
    )

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
    
    @property
    def app_name(self):
        if self.app:
            return self.app.name
        else:
            return ''

    natural_key.dependencies = ['contenttypes.contenttype']


class PermissionGroup(BaseModel):

    name = models.CharField(_('name'), max_length=255)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="permission_set",
        related_query_name="permission",
    )
    is_system_group = models.BooleanField(
        default=True,
        verbose_name='是否是系统组'
    )
    tenant = models.ForeignKey(
        Tenant,
        blank=False,
        null=True,
        default=None,
        on_delete=models.PROTECT
    )

    @property
    def permission_names(self):
        permissions = self.permissions.all()
        items = []
        for permission in permissions:
            items.append(permission.name)
        return items

    @property
    def permission_uuids(self):
        permissions = self.permissions.all()
        items = []
        for permission in permissions:
            items.append(permission.uuid)
        return items

    @property
    def permission_children(self):
        return self.permissions.all()

    def __str__(self) -> str:
        return self.name


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
    last_update_pwd = models.DateTimeField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        default=None,
        null=True,
        blank=True,
        verbose_name='父账号',
        on_delete=models.PROTECT,
    )
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
    user_permissions_group = models.ManyToManyField(
        'inventory.PermissionGroup',
        blank=True,
        related_name="user_permission_groups_set",
        related_query_name="user_permission_groups",
    )
    is_platform_user = models.BooleanField(default=False, verbose_name='是否是平台用户')

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
        from external_idp.models import ExternalIdp
        from extension.utils import find_available_extensions
        result = ''
        external_idps = ExternalIdp.valid_objects.order_by('order_no', 'id')
        available_extensions = find_available_extensions()
        for external_idp in external_idps:
            idp_type = external_idp.type
            for extension in available_extensions:
                extension_name = extension.name
                if idp_type == extension_name:
                    try:
                        items = extension.get_unbind_url(self)
                        if len(items) > 0:
                            result = '{}{} '.format(result,extension_name)
                    except:
                        print('没有启用插件，无法读取:'+extension_name)
        result = result.rstrip()
        return result

    @property
    def token(self):
        token, _ = Token.objects.get_or_create(
            user=self,
        )
        return token.key

    def account_type(self):
        if self.parent:
            return '子账号'
        else:
            return '主账号'

    def check_token(self, tenant_uuid):
        from extension_root.tenantuserconfig.models import TenantUserConfig

        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        config = TenantUserConfig.active_objects.filter(tenant=tenant).first()
        if config:
            data = config.data
            is_look_token = data['is_look_token']
            if is_look_token is True:
                return self.token
            else:
                return ""
        else:
            return ""

    def refresh_token(self):
        import datetime

        self.last_login = datetime.datetime.now()
        self.save()
        Token.objects.filter(user=self).delete()
        token, _ = Token.objects.get_or_create(user=self)
        return token

    @property
    def new_token(self):
        Token.objects.filter(user=self).delete()
        token, _ = Token.objects.get_or_create(user=self)
        return token.key

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password
        if self.id:
            UserPassword.valid_objects.get_or_create(
                user=self, password=self.md5_password(raw_password)
            )
        self.last_update_pwd = datetime.datetime.now()

    def valid_password(self, raw_password):
        return UserPassword.valid_objects.filter(
            user=self, password=self.md5_password(raw_password)
        ).exists()

    def md5_password(self, raw_password):
        for i in range(3):
            import hashlib

            hl = hashlib.md5()
            hl.update(raw_password.encode(encoding='utf-8'))
            hex_password = hl.hexdigest()
            raw_password = hex_password
        return hex_password

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
    
    def check_permission(self, tenant):
        '''
        检查用户是否是某个租户的管理员
        '''
        from extension_root.childmanager.models import ChildManager
        from django.http.response import JsonResponse
        from common.code import Code
        if self.is_superuser is False and tenant.has_admin_perm(self) is False and ChildManager.valid_objects.filter(tenant=tenant, user=self).exists() is False:
            return JsonResponse(
                data={
                    'error': Code.PERMISSION_ERROR.value,
                    'message': _('unauthorized operation'),
                }
            )
        else:
            return None

    
    def check_super_permission(self, tenant):
        '''
        检查用户是否是某个租户的超级管理员
        '''
        from extension_root.childmanager.models import ChildManager
        from django.http.response import JsonResponse
        from common.code import Code
        if self.is_superuser is False and tenant.has_admin_perm(self) is False:
            return JsonResponse(
                data={
                    'error': Code.PERMISSION_ERROR.value,
                    'message': _('unauthorized operation'),
                }
            )
        else:
            return None


class UserPassword(BaseModel):

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    password = models.CharField(max_length=128, blank=False, null=True)

    def __str__(self) -> str:
        return f'{self.user.username} - {self.password}'


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
    permissions_groups = models.ManyToManyField(
        'inventory.PermissionGroup',
        blank=True,
        related_name="permission_groups_set",
        related_query_name="permission_groups",
    )

    def __str__(self) -> str:
        return f'{self.name}'

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

    def child_groups(self, uuids):
        groups = Group.active_objects.filter(parent=self)
        if groups.exists() is False:
            return uuids
        for group in groups:
            uuids.append(str(group.uuid))
            group.child_groups(uuids)


class Invitation(BaseModel):
    '''
    注册邀请

    过期或接受邀请后进入invalid状态
    '''

    inviter = models.ForeignKey(
        'inventory.User',
        related_name='inviter',
        verbose_name='发起邀请者',
        on_delete=models.CASCADE,
    )
    invitee = models.ForeignKey(
        'inventory.User',
        related_name='invitee',
        verbose_name='被邀请者',
        on_delete=models.CASCADE,
    )
    duration = models.DurationField(
        default=datetime.timedelta(days=1), verbose_name='有效时长'
    )
    is_accepted = models.BooleanField(default=False, verbose_name='是否确认接受邀请')

    # active_objects = InvitationActiveManager()

    @property
    def expired_time(self):
        '''
        过期时间
        '''
        return self.duration + self.created

    @property
    def is_expired(self):
        '''
        是否过期
        '''
        return self.expired_time < timezone.now()

    @property
    def key(self):
        '''
        :rtype: string
        '''
        payload = {
            'uuid': self.uuid.hex,  # pylint: disable=no-member
            'company': 'singleton',
            'invitee_mobile': self.invitee.mobile,  # pylint: disable=no-member
            'timestamp': self.created.strftime(
                '%Y%m%d%H%M%s'
            ),  # pylint: disable=no-member
        }
        return KEY.encrypt(json.dumps(payload).encode()).decode('utf-8')

    @classmethod
    def parse(cls, key):
        '''
        解析key以获取邀请记录
        '''
        try:
            raw_paylod = KEY.decrypt(key.encode()).decode('utf-8')
        except InvalidToken:
            return None

        try:
            paylod = json.loads(raw_paylod)
        except json.JSONDecodeError:
            return None

        return cls.active_objects.filter(
            invitee__mobile=paylod.get('invitee_mobile', ''),
            uuid=paylod.get('uuid', ''),
        ).first()


class I18NMobileConfig(BaseModel):
    """
    国际手机号码接入配置
    """

    state = models.CharField(max_length=128, unique=True, verbose_name='号码归属区域')
    state_code = models.CharField(
        max_length=32, blank=False, null=False, unique=True, verbose_name='国家区号'
    )
    number_length = models.IntegerField(null=True, default=None, verbose_name='号码固定长度')
    start_digital = models.JSONField(default=[], blank=True, verbose_name='首位数字限制集')


class CustomField(BaseModel):
    '''
    自定义字段
    '''

    SUBJECT_CHOICES = (
        ('user', '用户'),  # '^[a-z]{1,16}$'
        ('group', '组'),
    )

    tenant = models.ForeignKey(
        'tenant.Tenant', blank=False, null=True, on_delete=models.PROTECT
    )
    name = models.CharField(max_length=128, verbose_name='字段名称')
    subject = models.CharField(
        choices=SUBJECT_CHOICES, default='user', max_length=128, verbose_name='字段分类'
    )
    schema = models.JSONField(default={'type': 'string'}, verbose_name='字段定义')
    is_visible = models.BooleanField(default=True, verbose_name='是否展示')


class NativeField(BaseModel):
    '''
    原生字段
    '''

    SUBJECT_CHOICES = (
        ('user', '内部联系人'),  # '^[a-z]{1,16}$'
        ('extern_user', '外部联系人'),
    )
    name = models.CharField(max_length=128, verbose_name='字段名称')
    key = models.CharField(max_length=256, verbose_name='内部字段名')
    subject = models.CharField(
        choices=SUBJECT_CHOICES, default='user', max_length=128, verbose_name='字段分类'
    )
    schema = models.JSONField(default={'type': 'string'}, verbose_name='字段定义')
    is_visible = models.BooleanField(default=True, verbose_name='是否展示')
    is_visible_editable = models.BooleanField(
        default=True, verbose_name='对于`是否展示`，是否可以修改'
    )


class CustomUser(BaseModel):
    '''
    定制化用户信息
    '''

    user = models.ForeignKey(
        'inventory.User',
        verbose_name='用户',
        related_name='custom_user',
        on_delete=models.CASCADE,
    )
    tenant = models.ForeignKey(
        'tenant.Tenant', blank=True, null=True, on_delete=models.CASCADE
    )
    data = models.JSONField(verbose_name='信息内容')

    # def update(self, **kwargs):
    #     '''
    #     更新数据
    #     '''
    #     self.data.update(**kwargs)    # pylint: disable=no-member
    #     self.save()

    # def pretty(self, visible_only=True):
    #     '''
    #     前端友好的输出
    #     '''
    #     # pylint: disable=no-member
    #     res = []
    #     data = self.data

    #     kwargs = {}
    #     if visible_only:
    #         kwargs.update(is_visible=True)

    #     for field in CustomField.valid_objects.filter(**kwargs):
    #         res.append({
    #             'uuid': field.uuid.hex,
    #             'name': field.name,
    #             'value': data.get(field.uuid.hex, ''),
    #         })
    #     return res


class UserAppData(BaseModel):
    '''
    用户APP数据
    '''

    DEFAULT_VALUE = ""

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='用户')
    data = models.JSONField(verbose_name='数据内容')

    def __str__(self) -> str:
        return f'User: {self.user.username}'
