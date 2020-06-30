"""
schema of AppGroup
"""
from django.db import models
from django.db.utils import IntegrityError

from common.django.model import BaseOrderedModel
from oneid_meta.models.mixin import TreeNode, NodeVisibilityScope
from oneid_meta.models.perm import PermOwnerMixin


class AppGroup(BaseOrderedModel, PermOwnerMixin, TreeNode, NodeVisibilityScope):
    """
    应用分组，SAAS版ArkID独有
    """
    NODE_PREFIX = 'ag_'

    uid = models.CharField(max_length=255, blank=False, verbose_name='APP分组的唯一标识')
    name = models.CharField(max_length=255, blank=False, default='', verbose_name='APP分组名称')
    remark = models.TextField(blank=True, default='', verbose_name='APP分组的详细介绍')
    parent = models.ForeignKey('oneid_meta.AppGroup', null=True, verbose_name='父级节点', on_delete=models.PROTECT)
    top = models.CharField(max_length=255, blank=True, default='root', verbose_name='范围的顶点uid')

    def __str__(self):
        return 'App Group: {}({})'.format(self.uid, self.name)

    def save(self, *args, **kwargs):
        if AppGroup.valid_objects.filter(uid=self.uid).exclude(pk=self.pk).exists():
            msg = "UNIQUE constraint failed: " \
                "oneid_meta.Group UniqueConstraint(fields=['uid'], condition=Q(is_del='False')"
            raise IntegrityError(msg)
        super(AppGroup, self).save(*args, **kwargs)

    @property
    def apps(self):
        """
        下属应用成员
        """
        return [item.app for item in AppGroupMember.valid_objects.filter(owner=self).order_by('order_no')]

    @property
    def app_groups(self):
        """
        下属子应用分组
        """
        return AppGroup.valid_objects.filter(parent=self).order_by('order_no')

    @property
    def children(self):
        """
        子节点
        """
        return self.app_groups

    @property
    def node_subject(self):
        """
        节点类型
        """
        return 'app_group'

    @property
    def is_root(self):
        """
        是否是根节点
        """
        return (self.parent is None) or self.uid == 'root'

    def if_belong_to_group(self, app_group, recursive):
        """
        判断是否属于某个组
        :param app_group:
        :param bool recursive: ”属于该组的子孙组“是否算“属于该组”
        """
        if self.parent is None:
            return False

        if self.parent == app_group:
            return True

        if recursive:
            return self.parent.if_belong_to_group(app_group, recursive)    # pylint: disable=no-member
        return False

    @property
    def member_cls(self):
        """
        成员关系类型
        """
        return AppGroupMember


class AppGroupMember(BaseOrderedModel):
    """
    应用分组与应用的从属关系
    这里组只收录末端应用分组
    """

    app = models.ForeignKey('oneid_meta.APP', on_delete=models.PROTECT)
    owner = models.ForeignKey('oneid_meta.AppGroup', verbose_name='所属应用分组', on_delete=models.PROTECT)

    class Meta:    # pylint: disable=missing-docstring
        unique_together = ('app', 'owner')

    def __str__(self):
        return f'AppGroupMember: {self.app} -> {self.owner}'
