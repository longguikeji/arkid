# pylint: disable=too-many-lines
'''
schema of Users
'''

# pylint: disable=too-many-lines
# pylint: disable=import-error
from itertools import chain

import django
import jsonfield
from django.core.cache import cache
from django.db import models
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from common.django.model import BaseModel, IgnoreDeletedManager
from oneid_meta.models.config import CustomField
from oneid_meta.models.group import GroupMember, Group
from oneid_meta.models.dept import DeptMember, Dept
from oneid_meta.models.perm import UserPerm, PermOwnerMixin, DeptPerm, GroupPerm
from oneid_meta.models.mixin import TreeNode as Node
from executer.utils.password import encrypt_password, verify_password
from infrastructure.utils.sms import is_mobile, is_native_mobile, is_i18n_mobile, is_cn_mobile, CN_MOBILE_PREFIX
if django.db.connection.vendor == "sqlite":
    from jsonfield import JSONField    # 测试环境（避免影响其他unit test）
else:
    from django_mysql.models import JSONField    # 生产、开发环境


class IsolatedManager(IgnoreDeletedManager):
    '''
    只返回独立账户
    '''
    def get_queryset(self):
        return super().get_queryset().filter(from_register=True)


class User(BaseModel, PermOwnerMixin):
    '''
    OneID 用户
    '''

    uuid = None

    class Meta:    # pylint: disable=missing-class-docstring
        indexes = [models.Index(fields=['username'], name='username_index')]

    GENDER_CHOICES = (
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    )
    ORIGIN_CHOICES = (
        (0, '脚本添加'),
        (1, '管理员添加'),
        (2, '用户名注册'),
        (3, '手机注册'),
        (4, '邮箱注册'),
    )
    username = models.CharField(max_length=255, blank=False, verbose_name='唯一标识')
    password = models.CharField(max_length=1024, blank=False, verbose_name='密码')
    name = models.CharField(max_length=255, blank=True, default='', verbose_name='姓名')
    email = models.CharField(max_length=255, blank=True, default='', verbose_name='邮箱')
    private_email = models.CharField(max_length=255, blank=True, default='', verbose_name='私人邮箱')    # 仅用于找回密码
    mobile = models.CharField(max_length=64, blank=True, default='', verbose_name='手机')
    # 支持 `18812341234`， `+86 18812341234` 两种格式

    employee_number = models.CharField(max_length=255, blank=True, default='', verbose_name='工号')
    position = models.CharField(max_length=255, blank=True, default='', verbose_name='职位')
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0, verbose_name='性别')
    avatar = models.CharField(max_length=1024, blank=True, default='', verbose_name='头像')
    is_boss = models.BooleanField(default=False, verbose_name='是否为主管理员')
    from_register = models.BooleanField(default=False, verbose_name='是否来自自己注册')
    origin = models.IntegerField(choices=ORIGIN_CHOICES, default=0, verbose_name='账号来源')
    hiredate = models.DateTimeField(blank=True, null=True, verbose_name='入职时间')
    remark = models.CharField(max_length=512, blank=True, default='', verbose_name='备注')
    last_active_time = models.DateTimeField(blank=True, null=True, verbose_name='最近活跃时间')
    require_reset_password = models.BooleanField(default=False, verbose_name='是否需要重置密码')

    isolated_objects = IsolatedManager()

    def save(self, *args, **kwargs):    # pylint: disable=arguments-differ,signature-differs
        for unique_feilds in [
                'username',
                'email',
                'mobile',
                'private_email',
        ]:
            value = getattr(self, unique_feilds)
            if not value:
                continue

            existed = False

            if unique_feilds == 'mobile':
                if not is_mobile(value):
                    raise ValidationError({unique_feilds: ['invalid']})

                if is_i18n_mobile(value) and is_cn_mobile(value):
                    existed = User.valid_objects.filter(
                        models.Q(mobile=value)
                        | models.Q(mobile=value.replace(CN_MOBILE_PREFIX, ""))).exclude(pk=self.pk).exists()    # pylint: disable=no-member
                elif is_native_mobile(value):
                    existed = User.valid_objects.filter(
                        models.Q(mobile=value)
                        | models.Q(mobile=CN_MOBILE_PREFIX + value)).exclude(pk=self.pk).exists()
                else:
                    existed = User.valid_objects.filter(mobile=value).exclude(pk=self.pk).exists()

            else:
                _kwargs = {unique_feilds: value}
                existed = User.valid_objects.filter(**_kwargs).exclude(pk=self.pk).exists()

            if existed:
                msg = "UNIQUE constraint failed: " + \
                        f"oneid_meta.User UniqueConstraint(fields=['{unique_feilds}'], condition=Q(is_del='False')"
                print(msg)
                raise ValidationError({unique_feilds: ['existed']})

        super(User, self).save(*args, **kwargs)

    @property
    def is_isolated(self):
        '''
        外部用户，用于各应用内部，不属于公司相关账户
        不等同于外部联系人
        目前先按是否是自己注册来区分
        '''
        return self.from_register

    @property
    def is_extern_user(self):    # pylint: disable=missing-docstring
        return GroupMember.valid_objects.filter(user=self, owner__uid='extern').exists()

    @is_isolated.setter
    def is_isolated(self, value):
        '''
        标记是否为外部用户
        '''
        self.from_register = value
        self.save()

    @property
    def display_name(self):
        '''
        用于展示的名称
        '''
        return self.name if self.name else self.username

    def __str__(self):
        return f'User: {self.username}({self.name})'

    @property
    def log_name(self):
        '''
        用于日志中的展示
        '''
        return f'{self.name}({self.username})'

    @classmethod
    def create_user(cls, username, password):
        '''
        创建用户
        '''
        return cls.objects.create(
            username=username,
            password=encrypt_password(password, settings.PASSWORD_ENCRYPTION),
        )

    @property
    def groups(self):
        '''
        用户直属组
        :rtype: list of Group
        '''
        return [item.owner for item in GroupMember.valid_objects.filter(user=self).select_related('owner')]

    @property
    def group_ids(self):
        '''
        用户直属组id
        '''
        return [item['owner_id'] for item in GroupMember.valid_objects.filter(user=self).values('owner_id')]

    @property
    def ding_depts(self):
        '''
        用户所在部门中与钉钉同步的部分
        :rtype: list of Group
        '''
        root_dept = Dept.objects.filter(uid='root').first()
        bind_ding_dept = []
        for dept in self.depts:
            if dept.if_belong_to_dept(root_dept, 1):
                bind_ding_dept.append(dept)
        return bind_ding_dept

    @property
    def ding_groups(self):
        '''
        用户所在角色中与钉钉同步的部分
        :rtype: list of Group
        '''
        role_group = Group.objects.filter(uid='role').first()
        bind_ding_group = []
        for group in self.groups:
            if group.if_belong_to_group(role_group, 1):
                bind_ding_group.append(group)
        return bind_ding_group

    @property
    def depts(self):
        '''
        用户直属部门
        :rtype: list of Dept
        '''
        return [item.owner for item in DeptMember.valid_objects.filter(user=self).select_related('owner')]

    @property
    def dept_ids(self):
        '''
        用户直属部门id
        '''
        return [item['owner_id'] for item in DeptMember.valid_objects.filter(user=self).values('owner_id')]

    @property
    def nodes(self):
        '''
        用户直属节点
        '''
        return chain(self.depts, self.groups)

    @property
    def perms(self):
        '''
        所有权限
        '''
        return UserPerm.valid_objects.filter(owner=self)

    def has_perm(self, perm):
        '''
        判断是否有某权限
        '''
        if perm is None:
            return True
        if self.is_admin:
            return True
        return UserPerm.valid_objects.filter(owner=self, perm=perm, value=True).exists()

    def has_perm_realtime(self, perm):
        '''
        实时判断是否有某权限
        适用于对权限结果准确度要求较高的场景
        '''
        if perm is None:
            return True
        if self.is_admin:
            return True

        user_perm = self.process_perm_realtime(perm)
        return user_perm.value

    def process_perm_realtime(self, perm):
        '''
        实时计算权限结果
        '''
        user_perm, _ = UserPerm.valid_objects.get_or_create(owner=self, perm=perm)

        dept_ids = [item.id for item in self.depts]
        user_perm.dept_perm_value = DeptPerm.valid_objects.filter(
            owner__id__in=dept_ids,
            perm=perm,
            status=1,
        ).exists()

        group_ids = [item.id for item in self.groups]
        user_perm.group_perm_value = GroupPerm.valid_objects.filter(
            owner__id__in=group_ids,
            perm=perm,
            status=1,
        ).exists()

        user_perm.save()

        user_perm.update_value()

        return user_perm

    def get_perm(self, perm):
        '''
        返回权限结果
        '''
        perm_result, _ = UserPerm.valid_objects.get_or_create(owner=self, perm=perm)
        return perm_result

    def if_belong_to_group(self, group, recursive):
        '''
        判断是否属于某个组
        :param bool recursive: ”属于该组的子孙组“是否算“属于该组”
        '''
        if recursive:
            raise NotImplementedError
        return GroupMember.valid_objects.filter(user=self, owner=group).exists()

    def if_belong_to_dept(self, dept, recursive):
        '''
        判断是否属于某一个部门
        :param bool recursive: ”属于该部门的子孙部门“是否算“属于该部门”
        '''
        if recursive:
            raise NotImplementedError
        return DeptMember.valid_objects.filter(user=self, owner=dept).exists()

    @property
    def dn(self):
        '''
        distinguish name
        '''
        return 'uid={},ou=people,{}'.format(self.username, settings.LDAP_BASE)

    @property
    def is_authenticated(self):    # pylint: disable=no-self-use
        '''
        always True
        adapt User to django
        '''
        return True

    @property
    def is_admin(self):
        '''
        是否是主管理员
        TODO: -> attr
        '''
        return self.username == 'admin' or self.is_boss

    @property
    def is_manager(self):
        '''
        是否是子管理员
        TODO: -> attr
        '''
        return GroupMember.valid_objects.filter(user=self, owner__manager_group__isnull=False).exists()

    @property
    def manager_groups(self):
        '''
        子管理员组 ManagerGroup
        '''
        for group_member in GroupMember.valid_objects.filter(user=self, owner__manager_group__isnull=False):
            yield group_member.owner.manager_group

    @property
    def token(self):
        '''
        return valid token
        '''
        return self.token_obj.key

    @property
    def token_obj(self):
        '''
        return valid token obj
        '''
        from drf_expiring_authtoken.models import ExpiringToken    # pylint: disable=import-outside-toplevel
        token, _ = ExpiringToken.objects.get_or_create(user=self)
        return token

    def refresh_token(self):
        '''
        使当前token失效，并返回新的token
        '''
        self.revoke_token()
        return self.token_obj

    def revoke_token(self):
        '''
        使当前token失效，不生成新的token
        '''
        from drf_expiring_authtoken.models import ExpiringToken    # pylint: disable=import-outside-toplevel
        token = ExpiringToken.objects.filter(user=self).first()
        if token:
            token.delete()

    @property
    def is_settled(self):
        '''
        是否已激活
        是否是入驻的用户
        对于导入、或者手动添加的用户，在真实用户未登录前，均视为未激活用户
        '''
        return bool(self.last_active_time)

    @property
    def has_password(self):
        '''
        是否有密码
        没有密码的情况，仅包括 管理员后台添加用户时未设置密码，此用户在激活设置密码前
        '''
        return self.password != ""

    @property
    def uid(self):
        '''
        唯一标识
        '''
        return self.username

    @property
    def owner_perm_cls(self):
        '''
        权限结果类型
        '''
        return UserPerm

    @property
    def node_uids(self):
        '''
        所有直属节点的uid
        '''
        key = f'oneid:user:{self.username}:parent_node'
        cache_data = cache.get(key)
        if cache_data is None:
            res = set([node.node_uid for node in self.depts] + [node.node_uid for node in self.groups])
            cache.set(key, res)
            return res
        return cache_data

    @property
    def all_node_uids(self):
        '''
        所有直属节点以及隶属节点的uid
        '''
        key = f'oneid:user:{self.username}:upstream_node'
        cache_data = cache.get(key)
        if cache_data is None:
            res = set()
            for parent_node in Node.retrieve_nodes(self.node_uids):
                res.update(parent_node.upstream_uids)
            cache.set(key, res)
            return res
        return cache_data

    def update_cache(self):
        '''
        更新缓存
        '''
        cache.delete(f'oneid:user:{self.username}:parent_node')
        _ = self.node_uids

        cache.delete(f'oneid:user:{self.username}:upstream_node')
        _ = self.all_node_uids

    def under_manage(self, user):
        '''
        是否在某人管理之下
        '''
        if user.is_admin:
            return True
        self_all_node_uids = self.all_node_uids
        for manager_group in user.manager_groups:
            if manager_group.scope_subject == 2:    # 指定节点、人
                for node in self.nodes:
                    if node.under_manage(user):
                        return True
                if self.username in manager_group.users:
                    return True
            if manager_group.scope_subject == 1:    # 所在节点
                if self_all_node_uids & user.node_uids:
                    return True
        return False

    def is_visible_to_manager(self, user):
        '''
        校验指定管理员是否可见此人
        '''
        if user.is_admin:
            return True
        self_all_node_uids = self.all_node_uids
        for manager_group in user.manager_groups:
            if self.username in manager_group.users:
                return True
            if self_all_node_uids & set(manager_group.nodes):
                return True
            if manager_group.scope_subject == 1 and (user.all_manage_node_uids & self_all_node_uids):
                return True
        return False

    def is_visible_to_employee(self, user):
        '''
        校验指定员工是否可见此人
        '''
        if self == user:
            return True
        for node in self.nodes:
            if node.is_open_to_employee(user):
                # 节点对某人开放，意味着此人可以看到该节点成员
                return True
        return False

    @property
    def manage_node_uids(self):
        '''
        直接管理的节点（不包含下级）
        '''
        res = set()
        for manager_group in self.manager_groups:
            if manager_group.scope_subject == 2:    # 指定节点、人
                res.update(manager_group.nodes)
                continue
            if manager_group.scope_subject == 1:    # 所在节点
                res.update(self.node_uids)
        return res

    @property
    def manage_user_uids(self):
        '''
        直接管理的人员(不包括从管理组继承而来的可管理的人)
        '''
        res = set()
        for manager_group in self.manager_groups:
            if manager_group.scope_subject == 2:    # 指定节点、人
                res.update(manager_group.users)
        return res

    @property
    def all_manage_node_uids(self):
        '''
        所有可管理的节点（包含直接管理的节点，及其下属节点）
        '''
        res = set()
        for node_uid in self.manage_node_uids:
            res.update(Node.get_downstream_uids(node_uid))

        # 过滤根节点管理权限
        discard_node = {'g_root', 'g_manager', 'g_extern', 'g_intra'}
        for node in discard_node:
            res.discard(node)
        return res

    def check_password(self, password):
        '''
        校验密码是否正确
        :rtype: boolean
        '''
        return verify_password(password, self.password)

    @property
    def origin_verbose(self):
        '''
        账号来源
        '''
        return self.ORIGIN_CHOICES[self.origin][1]    # pylint: disable=invalid-sequence-index

    @property
    def is_intra(self):
        '''
        是否为内部员工
        '''
        # bad implement
        return not GroupMember.valid_objects.filter(owner__uid='extern', user=self).exists()

    def update_last_active_time(self, gap_minutes=5):
        '''
        最近活跃时间
        '''
        now = timezone.now()
        if not self.last_active_time or \
            self.last_active_time + timezone.timedelta(minutes=gap_minutes) < now:
            self.last_active_time = now
            self.save(update_fields=['last_active_time'])

    @property
    def aliyun_sso_roles(self):
        """与阿里云角色sso相关联信息"""
        # pylint: disable=no-member
        return self.aliyun_sso_role.role if self.aliyun_sso_role.is_active else []

    @property
    def aliyun_sso_session_duration(self):
        """与阿里云角色sso相关联信息"""
        # pylint: disable=no-member
        return str(self.aliyun_sso_role.session_duration)


class PosixUser(BaseModel):
    '''
    服务器用户
    '''
    user = models.OneToOneField(User, verbose_name='用户', related_name='posix_user', on_delete=models.PROTECT)
    uid = models.IntegerField(blank=True, default=500)
    gid = models.IntegerField(blank=True, default=500)
    home = models.CharField(max_length=255, blank=True, default='', verbose_name='家目录')
    pub_key = models.CharField(max_length=255, blank=True, default='', verbose_name='公钥')


class CustomUser(BaseModel):
    '''
    定制化用户信息
    '''
    DEFAULT_VALUE = ""

    user = models.OneToOneField(User, verbose_name='用户', related_name='custom_user', on_delete=models.CASCADE)
    data = JSONField(verbose_name='信息内容')

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

        if self.user.is_intra:
            for field in CustomField.valid_objects.filter(subject='user', **kwargs):
                res.append({
                    'uuid': field.uuid.hex,
                    'name': field.name,
                    'value': data.get(field.uuid.hex, ''),
                })
            for field in CustomField.valid_objects.filter(subject='extern_user', **kwargs):
                if field.uuid.hex in data:    # pylint: disable=unsupported-membership-test
                    res.append({
                        'uuid': field.uuid.hex,
                        'name': field.name,
                        'value': data.get(field.uuid.hex),
                    })
        else:
            for field in CustomField.valid_objects.filter(subject='extern_user', **kwargs):
                res.append({
                    'uuid': field.uuid.hex,
                    'name': field.name,
                    'value': data.get(field.uuid.hex, ''),
                })
            for field in CustomField.valid_objects.filter(subject='user', **kwargs):
                if field.uuid.hex in data:    # pylint: disable=unsupported-membership-test
                    res.append({
                        'uuid': field.uuid.hex,
                        'name': field.name,
                        'value': data.get(field.uuid.hex),
                    })
        return res


class DingUser(BaseModel):
    '''
    钉钉用户
    '''
    user = models.OneToOneField(User, verbose_name='用户', related_name='ding_user', on_delete=models.PROTECT)
    account = models.CharField(max_length=64, blank=True, verbose_name='钉钉账号(手机)')
    uid = models.CharField(max_length=255, blank=True, verbose_name='员工在企业内的唯一标识')
    data = models.TextField(blank=True, default='{}', verbose_name='钉钉员工详细数据(JSON)')
    ding_id = models.TextField(max_length=255, blank=True, verbose_name='钉钉ID')
    open_id = models.TextField(max_length=255, blank=True, verbose_name='用户在当前开放应用内的唯一标识')
    union_id = models.TextField(max_length=255, blank=True, verbose_name='用户在当前开放应用所属的钉钉开放平台账号内的唯一标识')


class AlipayUser(BaseModel):
    '''
    支付宝用户
    '''
    user = models.OneToOneField(User, verbose_name='用户', related_name='alipay_user', on_delete=models.PROTECT)
    alipay_user_id = models.TextField(max_length=255, blank=True, verbose_name='支付宝ID')


class WorkWechatUser(BaseModel):
    '''
    企业微信用户
    '''
    user = models.OneToOneField(User, verbose_name='用户', related_name='work_wechat_user', on_delete=models.PROTECT)
    work_wechat_user_id = models.TextField(max_length=255, blank=True, verbose_name='企业微信ID')


class WechatUser(BaseModel):
    '''
    微信用户
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        indexes = [models.Index(fields=['unionid'], name='wechatunionid_index')]

    user = models.OneToOneField(User, verbose_name='用户', related_name='wechat_user', on_delete=models.PROTECT)
    unionid = models.CharField(max_length=255, blank=True, verbose_name='用户OPENID')


class QQUser(BaseModel):
    '''
    qq用户绑定表
    '''
    user = models.OneToOneField(User, verbose_name='用户', related_name='qq_user', on_delete=models.PROTECT)
    open_id = models.TextField(max_length=255, blank=True, verbose_name='qq平台openid')


class GithubUser(BaseModel):
    """
    github用户
    """
    class Meta:    # pylint: disable=missing-class-docstring
        indexes = [models.Index(fields=['github_user_id'], name='githubuserid_index')]

    user = models.OneToOneField(User, verbose_name='用户', related_name='github_user', on_delete=models.PROTECT)
    github_user_id = models.CharField(max_length=255, blank=True, verbose_name='Github ID')


class SubAccount(BaseModel):
    '''
    子账号
    '''
    domain = models.CharField(max_length=255, verbose_name='登录域名')
    username = models.CharField(max_length=255, default="", null=True, verbose_name='用户名')
    password = models.CharField(max_length=512, verbose_name='密码、token')


class AliyunSSORole(BaseModel):
    """
    阿里云角色SSO与user对接信息
    """
    user = models.OneToOneField(User, verbose_name='用户', related_name='aliyun_sso_role', on_delete=models.CASCADE)
    role = jsonfield.JSONField(default=[], blank=True, verbose_name='阿里云SSO角色分配')
    session_duration = models.IntegerField(blank=True, default=900)
