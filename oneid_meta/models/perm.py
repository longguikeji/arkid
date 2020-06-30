'''
schema of Perms

GroupPerm, DeptPerm实时更新
UserPerm存在一定延迟
'''
# pylint: disable=too-many-lines,import-outside-toplevel, cyclic-import
import re

from django.db import models

from common.django.model import BaseModel


class Perm(BaseModel):
    '''
    权限
    一方面来自应用
    也可脱离应用自行定义
    '''
    pattern = r'^[\d|a-z]+_\$?[-|\d|a-z]+_[\d|a-z]+$'

    uid = models.CharField(unique=True, max_length=255, blank=True, null=False, default='', verbose_name='权限唯一标识')
    name = models.CharField(max_length=255, blank=False, default='', verbose_name='权限名称')
    remark = models.TextField(blank=True, default='', verbose_name='详细介绍')
    scope = models.CharField(max_length=128, blank=False, verbose_name='权限作用域')
    action = models.CharField(max_length=128, blank=True, default='', verbose_name='操作行为')
    subject = models.CharField(max_length=255, blank=True, default='app', verbose_name='权限分类')

    sub_account = models.ForeignKey("oneid_meta.SubAccount",
                                    blank=True,
                                    null=True,
                                    verbose_name='子账号',
                                    on_delete=models.CASCADE)

    editable = models.BooleanField(default=True, verbose_name='是否可编辑、删除')    # access 和 部分系统层面的perm无法修改
    default_value = models.BooleanField(default=False, verbose_name='默认授权还是拒绝')

    # 当做只有一级分类简化处理，若有多级分类，以`.`分隔，自行处理。不提供目录树的操作。
    # default_uid = '{}_{}_{}'.format(subject + scope + action)

    def __str__(self):
        return f'Perm: {self.uid}({self.name})'

    def save(self, *args, **kwargs):    # pylint: disable=arguments-differ
        '''
        auto uid
        '''
        if not self.id and not self.uid:    # pylint: disable=no-member
            self.uid = '{}_{}_{}'.format(self.subject, self.scope, self.action)
        super(Perm, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        perm 硬删除
        userperm,groupperm,deptperm 联级硬删除
        '''
        self.kill()

    @classmethod
    def get(cls, uid):
        '''
        shortcut for get_or_create
        '''
        if not re.match(cls.pattern, uid):
            # return None
            raise ValueError(f"invalid perm uid, must match: `{cls.pattern}`")

        perm = cls.valid_objects.filter(uid=uid).first()
        if perm:
            return perm

        subject, scope, action = uid.split('_')
        return Perm.objects.create(subject=subject, scope=scope, action=action)

    @property
    def app(self):
        '''
        权限所属的应用
        '''
        from oneid_meta.models import APP    # pylint: disable=import-outside-toplevel
        if self.subject == 'app':
            return APP.valid_objects.filter(uid=self.scope).first()


class PermOwnerMixin():
    '''
    权限所有者
    '''
    @property
    def owner_perm_cls(self):
        '''
        权限结果类型
        '''
        raise NotImplementedError


class OwnerPerm(BaseModel):
    '''
    某类对象和具体权限的关系
    '''
    class Meta:    # pylint: disable=missing-docstring
        abstract = True
        unique_together = ("owner", "perm")

    STATUS_CHOICES = (
        (-1, '显式拒绝'),
        (0, '随上级决定'),
        (1, '显式授权'),
    )

    VALUE_CHOICES = (
        (-1, False),
        (1, True),
    )

    owner = models.ForeignKey('oneid_meta.User', on_delete=models.CASCADE)
    perm = models.ForeignKey(Perm, verbose_name='权限', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='授权状态')
    value = models.BooleanField(default=False, verbose_name='是否有权限')

    def __str__(self):
        return f'{self.__class__.__name__}: {self.owner} -> {self.perm} = {self.value}'

    def permit(self):
        '''
        显式授权
        '''
        self.status = 1
        self.value = True
        self.save()

    def reject(self):
        '''
        显式拒绝
        '''
        self.status = -1
        self.value = False
        self.save()

    def boggle(self):
        '''
        随上级决定
        '''
        # pylint: disable=no-member
        self.status = 0
        if self.owner.is_root:
            self.value = False
        else:
            self.value = self.owner.parent.get_perm(self.perm).value
        self.save()

    @property
    def locked(self):
        '''
        是否可以修改value
        目前始终可以修改
        '''
        return False
        # # pylint: disable=no-member
        # return isinstance(self, (GroupPerm, DeptPerm)) and \
        #     bool(self.owner.parent) and \
        #     self.__class__.valid_objects.filter(owner=self.owner.parent, perm=self.perm, value=True).exists()

    def update_status(self, status):
        '''
        更新授权状态，用于group、dept
        当授权结果发生变化时，会修改子孙节点
        '''
        # pylint: disable=no-member
        # former_status = self.status
        # next_status = status
        # self.status = next_status
        # self.save()

        # if former_status == 0 and next_status == 1:
        #     if not self.value:    # False -> True
        #         for node in self.owner.tree_front_walker():
        #             node_perm = node.get_perm(self.perm)
        #             if not node_perm.value:
        #                 node_perm.value = True
        #                 node_perm.save()

        # if former_status == 1 and next_status == 0:
        #     if self.owner.is_root:
        #         parent_value = False
        #     else:
        #         parent_value = self.owner.parent.get_perm_value(self.perm)
        #     if not parent_value:    # True -> False
        #         for node in self.owner.tree_front_walker():
        #             node_perm = node.get_perm(self.perm)
        #             if node_perm.value:
        #                 node_perm.value = False
        #                 node_perm.save()

        self.status = status
        self.update_value()
        self.save()

    def update_value(self):
        '''
        根据自身status和上级value更新自身value
        '''
        # pylint: disable=no-member
        if self.status == 0:
            self.boggle()
        else:
            self.value = self.status == 1
        self.save()

    def delete(self, *args, **kwargs):
        '''
        硬删除
        '''
        self.kill()

    @property
    def owner_subject(self):
        '''
        所有者类型
        '''
        raise NotImplementedError

    @property
    def owner_cls(self):
        '''
        所有者类型 class
        '''
        raise NotImplementedError

    @property
    def owner_uid(self):
        '''
        所有者uid，在所有owner间并不唯一
        '''
        raise NotImplementedError

    @staticmethod
    def get(owner, perm):
        '''
        retrieve
        '''
        owner_perm, _ = owner.owner_perm_cls.valid_objects.get_or_create(perm=perm, owner=owner)
        return owner_perm


class GroupPerm(OwnerPerm):
    '''
    组和权限的关系
    只能随上级决定或显式授权
    无法显式拒绝
    '''

    owner = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE)

    @property
    def owner_subject(self):
        return self.owner.node_subject    # pylint: disable=no-member

    @property
    def owner_uid(self):
        return self.owner.node_uid    # pylint: disable=no-member

    @property
    def owner_cls(self):
        '''
        所有者类型 class
        '''
        from oneid_meta.models import Group    # pylint: disable=import-outside-toplevel
        return Group


class AppGroupPerm(OwnerPerm):
    """
    应用分组和权限的关系 TODO 未来可考虑兼容oauth（细粒度应用权限）
    只能随上级决定或显式授权
    无法显式拒绝
    """

    owner = models.ForeignKey('oneid_meta.AppGroup', on_delete=models.CASCADE)

    @property
    def owner_subject(self):
        return self.owner.node_subject    # pylint: disable=no-member

    @property
    def owner_uid(self):
        return self.owner.node_uid    # pylint: disable=no-member

    @property
    def owner_cls(self):
        """
        所有者类型 class
        """
        from oneid_meta.models import AppGroup    # pylint: disable=import-outside-toplevel
        return AppGroup


class DeptPerm(OwnerPerm):
    '''
    组和权限的关系
    只能随上级决定或显式授权
    无法显式拒绝
    '''

    owner = models.ForeignKey('oneid_meta.Dept', on_delete=models.CASCADE)

    @property
    def owner_subject(self):
        '''
        所有者类型
        '''
        return self.owner.node_subject    # pylint: disable=no-member

    @property
    def owner_uid(self):
        return self.owner.node_uid    # pylint: disable=no-member

    @property
    def owner_cls(self):
        '''
        所有者类型 class
        '''
        from oneid_meta.models import Dept    # pylint: disable=import-outside-toplevel
        return Dept


class UserPerm(OwnerPerm):
    '''
    用户和权限的关系
    随上级决定时，部门或组任意单位有权限，即可继承权限
    另可显式拒绝 或 显式授权
    '''

    owner = models.ForeignKey('oneid_meta.User', on_delete=models.CASCADE)

    dept_perm_value = models.BooleanField(default=False, verbose_name='部门权限校验结果')
    group_perm_value = models.BooleanField(default=False, verbose_name='组权限校验结果')

    def boggle(self):
        '''
        随上级决定
        '''
        self.status = 0
        self.value = self.node_perm_value
        self.save()

    @property
    def owner_subject(self):
        '''
        所有者类型
        '''
        return 'user'

    @property
    def owner_uid(self):
        return self.owner.username    # pylint: disable=no-member

    @property
    def node_perm_value(self):
        '''
        分组权限判定结果
        '''
        return self.dept_perm_value or self.group_perm_value

    @property
    def owner_cls(self):
        '''
        所有者类型 class
        '''
        from oneid_meta.models import User    # pylint: disable=import-outside-toplevel
        return User
