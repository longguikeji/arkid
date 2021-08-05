'''
scheme of Departments
'''
import jsonfield
import django
from django.db import models
from django.conf import settings
from django.db.utils import IntegrityError

from common.django.model import BaseOrderedModel, BaseModel
from oneid_meta.models.perm import DeptPerm, PermOwnerMixin
from oneid_meta.models.mixin import TreeNode, NodeVisibilityScope

if django.db.connection.vendor == "sqlite":
    from jsonfield import JSONField    # 测试环境（避免影响其他unit test）
else:
    from django_mysql.models import JSONField    # 生产、开发环境

class Dept(BaseOrderedModel, PermOwnerMixin, TreeNode, NodeVisibilityScope):
    '''
    OneID 部门
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        indexes = [models.Index(fields=['uid'], name='dept_uid_index')]

    NODE_PREFIX = 'd_'

    uid = models.CharField(max_length=255, blank=False, verbose_name='唯一标识')
    name = models.CharField(max_length=255, blank=False, verbose_name='部门名称')
    remark = models.TextField(default='', blank=True, verbose_name='详细介绍')
    parent = models.ForeignKey('oneid_meta.Dept', null=True, verbose_name='父级节点', on_delete=models.PROTECT)

    def __str__(self):
        return f'Dept: {self.uid}({self.name})'

    def save(self, *args, **kwargs):    # pylint: disable=arguments-differ
        if Dept.valid_objects.filter(uid=self.uid).exclude(pk=self.pk).exists():
            msg = "UNIQUE constraint failed: " \
                "oneid_meta.Dept UniqueConstraint(fields=['uid'], condition=Q(is_del='False')"
            raise IntegrityError(msg)

        super(Dept, self).save(*args, **kwargs)

    @property
    def is_top(self):
        '''
        是否为范围顶点
        '''
        return self.uid == self.top

    @property
    def top(self):
        '''
        可操作范围内的顶点
        '''
        return 'root'

    @property
    def node_subject(self):
        '''
        节点类型
        '''
        return 'dept'

    @property
    def users(self):
        '''
        下属成员
        '''
        return [
            item.user
            for item in DeptMember.valid_objects.filter(owner=self).order_by('order_no').select_related('user')
        ]

    _perms = None
    @property
    def perms(self):
        '''
        所有权限
        '''
        if not self._perms:
            self._perms = DeptPerm.valid_objects.filter(owner=self)
        return self._perms

    _depts = None
    @property
    def depts(self):
        '''
        下属子部门
        '''
        if not self._depts:
            self._depts = Dept.valid_objects.filter(parent=self).order_by('order_no')
        return self._depts

    def if_belong_to_dept(self, dept, recursive):
        '''
        判断是否属于某个部门
        :param bool recursive: ”属于该部门的子孙部门“是否算“属于该部门”
        '''
        if self.parent is None:
            return False

        if self.parent == dept:
            return True

        if recursive:
            return self.parent.if_belong_to_dept(dept, recursive)    # pylint: disable=no-member
        return False

    @property
    def dn(self):
        '''
        distinguish name
        在涉及修改dn的操作时禁止使用，自行在ldap中根据cn=uid查询dn
        '''
        if self.uid == 'root':
            return 'ou=dept,{}'.format(settings.LDAP_BASE)
        if self.parent:
            return 'cn={},{}'.format(self.uid, self.parent.dn)    # pylint: disable=no-member
        return 'cn={},ou=dept,{}'.format(self.uid, settings.LDAP_BASE)

    @property
    def children(self):
        '''
        子节点
        '''
        return self.depts

    def get_perm_value(self, perm):
        '''
        查询对某一权限有无授权
        '''
        return self.get_perm(perm).value

    def get_perm(self, perm):
        '''
        返回权限结果
        '''
        perm_result, _ = DeptPerm.valid_objects.get_or_create(owner=self, perm=perm)
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
    def parents(self):
        '''
        上级节点，离自己近的在前，不包括自己，除root返回[]外，其余节点最后一项必为root
        '''
        if self.parent is None:
            return []
        return [self.parent] + self.parent.parents    # pylint: disable=no-member

    @property
    def member_cls(self):
        '''
        成员关系类型
        '''
        return DeptMember

    @property
    def owner_perm_cls(self):
        '''
        权限结果类型
        '''
        return DeptPerm

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


class CustomDept(BaseModel):
    dept = models.OneToOneField(Dept, verbose_name='Dept', related_name='custom_dept', on_delete=models.CASCADE)
    data = JSONField(verbose_name='扩展信息')


class DingDept(BaseOrderedModel):
    '''
    钉钉部门
    '''

    dept = models.OneToOneField('oneid_meta.Dept', related_name='ding_dept', on_delete=models.PROTECT)
    uid = models.IntegerField(blank=False, verbose_name='钉钉部门id')
    data = models.TextField(blank=True, default='{}', verbose_name='钉钉部门详细数据(JSON)')


class DeptMember(BaseOrderedModel):
    '''
    部门与用户的从属关系
    这里部门仅收录末端部门
    '''

    user = models.ForeignKey('oneid_meta.User', on_delete=models.PROTECT)
    owner = models.ForeignKey(Dept, verbose_name='所属部门', on_delete=models.PROTECT)

    class Meta:    # pylint: disable=missing-docstring
        unique_together = ('user', 'owner')

    def __str__(self):
        return f'DeptMember: {self.user} -> {self.owner}'
