'''
schema of Groups
'''
import jsonfield
from django.db import models
from django.conf import settings
from django.db.utils import IntegrityError

from common.django.model import BaseOrderedModel, BaseModel
from oneid_meta.models.org import Org
from oneid_meta.models.perm import GroupPerm, PermOwnerMixin
from oneid_meta.models.mixin import TreeNode, NodeVisibilityScope


class Group(BaseOrderedModel, PermOwnerMixin, TreeNode, NodeVisibilityScope):
    '''
    OneID组
    - 在Noah、钉钉中表现为角色
    - 在LDAP中表现为组
    '''

    NODE_PREFIX = 'g_'

    uid = models.CharField(max_length=255, blank=False, verbose_name='唯一标识')
    remark = models.TextField(default='', blank=True, verbose_name='选项介绍')
    name = models.CharField(max_length=255, blank=False, verbose_name='组名称')
    parent = models.ForeignKey('oneid_meta.Group', null=True, verbose_name='父级节点', on_delete=models.PROTECT)
    accept_user = models.BooleanField(blank=True, default=True)    # 是否接纳人员，对于角色组为否 deprecated TODO: delete this field

    top = models.CharField(max_length=255, blank=True, default='root', verbose_name='范围顶点uid')

    def __str__(self):
        return f'Group: {self.uid}({self.name})'

    def save(self, *args, **kwargs):    # pylint: disable=arguments-differ
        if Group.valid_objects.filter(uid=self.uid).exclude(pk=self.pk).exists():
            msg = "UNIQUE constraint failed: " \
                "oneid_meta.Group UniqueConstraint(fields=['uid'], condition=Q(is_del='False')"
            raise IntegrityError(msg)
        super(Group, self).save(*args, **kwargs)

    @property
    def node_subject(self):
        '''
        节点类型
        Group中定义为范围顶点的uid
        '''
        if Org.valid_objects.filter(group=self).exists():
            return 'org'
        if Org.valid_objects.filter(role__uid=self.top).exists():
            return 'role'
        if Org.valid_objects.filter(manager__uid=self.top).exists():
            return 'manager'
        if Org.valid_objects.filter(label__uid=self.top).exists():
            return 'label'
        if Org.valid_objects.filter(direct__uid=self.top).exists():
            return 'direct'
        return self.top

    @property
    def users(self):
        '''
        下属成员
        '''
        return [item.user for item in GroupMember.valid_objects.filter(owner=self).order_by('order_no')]

    @property
    def groups(self):
        '''
        下属子组
        '''
        return Group.valid_objects.filter(parent=self).order_by('order_no')

    @property
    def dn(self):
        '''
        distinguish name
        在涉及修改dn的操作时慎用，自行在ldap中根据cn=uid查询dn
        '''
        if self.uid == 'root':
            return 'ou=group,{}'.format(settings.LDAP_BASE)
        if self.parent:
            return 'cn={},{}'.format(self.uid, self.parent.dn)    # pylint: disable=no-member
        return 'cn={},ou=group,{}'.format(self.uid, settings.LDAP_BASE)

    @property
    def children(self):
        '''
        子节点
        '''
        return self.groups

    @property
    def perms(self):
        '''
        所有权限
        '''
        return GroupPerm.valid_objects.filter(owner=self)

    def if_belong_to_group(self, group, recursive):
        '''
        判断是否属于某个组
        :param bool recursive: ”属于该组的子孙组“是否算“属于该组”
        '''
        if self.parent is None:
            return False

        if self.parent == group:
            return True

        if recursive:
            return self.parent.if_belong_to_group(group, recursive)    # pylint: disable=no-member
        return False

    def get_perm_value(self, perm):
        '''
        查询对某一权限有无授权
        '''
        return self.get_perm(perm).value

    def get_perm(self, perm):
        '''
        返回权限结果
        '''
        perm_result, _ = GroupPerm.valid_objects.get_or_create(owner=self, perm=perm)
        return perm_result

    @property
    def is_root(self):
        '''
        是否是根节点
        '''
        return (self.parent is None) or self.uid == 'root'

    @classmethod
    def get_root(cls):
        '''
        返回根节点
        '''
        return cls.valid_objects.get(uid='root')

    @property
    def member_cls(self):
        '''
        成员关系类型
        '''
        return GroupMember

    @property
    def owner_perm_cls(self):
        '''
        权限结果类型
        '''
        return GroupPerm

    @property
    def detail_serializer_cls(self):
        '''
        详情序列化类
        '''
        from siteapi.v1.serializers.dept import DeptDetailSerializer    # pylint: disable=import-outside-toplevel
        return DeptDetailSerializer

    @property
    def detail_serializer(self):
        '''
        详情序列化实例
        '''
        return self.detail_serializer_cls(self)

    @classmethod
    def get_extern_root(cls):
        '''
        外部联系人根节点
        '''
        group, _ = cls.valid_objects.get_or_create(uid='extern')
        return group


class DingGroup(BaseModel):
    '''
    钉钉角色与角色组
    '''
    SUBJECT_CHOICES = (
        ('role', '角色与角色组（内部人员）'),
        ('label', '标签与标签组（外部人员）'),
    )
    group = models.OneToOneField('oneid_meta.Group', related_name='ding_group', on_delete=models.PROTECT)
    uid = models.IntegerField(blank=False, verbose_name='钉钉角色id')
    data = models.TextField(blank=True, default='{}', verbose_name='钉钉角色详细信息(JSON)')
    subject = models.CharField(choices=SUBJECT_CHOICES, max_length=128, default='role', verbose_name='组类型')
    is_group = models.BooleanField(default=False, verbose_name='区分角色组与角色，标签与标签组')


class ManagerGroup(BaseModel):
    '''
    Group的特殊形式，用于组织管理员
    - 应用权限的集合
    - 组织架构权限的集合
    '''

    SCOPE_SUBJECT_CHOICES = ((1, '所在节点及下级节点'), (2, '指定节点和人员'))

    group = models.OneToOneField('oneid_meta.Group', related_name='manager_group', on_delete=models.CASCADE)

    nodes = jsonfield.JSONField(default=[], blank=True, verbose_name='节点uids')
    users = jsonfield.JSONField(default=[], blank=True, verbose_name='人员uids')
    apps = jsonfield.JSONField(default=[], blank=True, verbose_name='应用uids')
    perms = jsonfield.JSONField(default=[], blank=True, verbose_name='权限uids')
    scope_subject = models.IntegerField(default=1, choices=SCOPE_SUBJECT_CHOICES, verbose_name='管理范围类型')


class GroupMember(BaseOrderedModel):
    """
    组与用户的从属关系
    这里组只收录末端组
    """

    user = models.ForeignKey('oneid_meta.User', on_delete=models.PROTECT)
    owner = models.ForeignKey('oneid_meta.Group', verbose_name='所属组', on_delete=models.PROTECT)

    class Meta:    # pylint: disable=missing-docstring
        unique_together = ('user', 'owner')

    def __str__(self):
        return f'GroupMember: {self.user} -> {self.owner}'
