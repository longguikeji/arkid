'''
Mixin for models
'''
from itertools import chain

from django.core.cache import cache
from django.db import models
import jsonfield


class NodeVisibilityScope(models.Model):
    '''
    节点对员工的可见范围
    '''
    class Meta:
        abstract = True

    VISIBILITY_SUBJECT = (    # 此处`对...可见`，为`对...开放`的意思，即使判定不可见，最终也有可能可以看到
        (1, '所有人可见'),    # 同一组织内所有人
        (2, '节点成员可见'),
        (3, '节点成员及其下属节点均可见'),
        (4, '只对指定人、节点可见'),
        (5, '所有人不可见'),
    )
    visibility = models.IntegerField(choices=VISIBILITY_SUBJECT, default=1, blank=True, verbose_name='可见范围类型')
    node_scope = jsonfield.JSONField(default=[], blank=True, verbose_name='指定节点node_uids')
    user_scope = jsonfield.JSONField(default=[], blank=True, verbose_name='指定人usernames')

    def is_open_to_employee(self, user):
        '''
        对user是否开放，由自身性质决定
        TODO: 优化
        '''
        if self.visibility == 1:
            if self.org:
                return self.org in user.organizations
            return True

        if self.visibility == 5:
            return False

        if self.visibility == 2:
            return self.member_cls.valid_objects.filter(owner=self, user=user).exists()    # pylint: disable=no-member

        if self.visibility == 3:
            node_uids = map(lambda node: node.uid, self.tree_front_walker())    # pylint: disable=no-member
            return self.member_cls.valid_objects.filter(user=user, owner__uid__in=node_uids).exists()

        if self.visibility == 4:
            if self.org:
                if self.org not in user.organizations:
                    return False
                self.node_scope = (uid for uid in self.user_scope if self.retrieve_node(uid).org.uuid == self.org.uuid)

            if user.username in self.user_scope:    # pylint: disable=no-member, unsupported-membership-test
                return True
            if self.member_cls.valid_objects.filter(user=user, owner__uid__in=self.node_scope).exists():    # pylint: disable=no-member
                return True
            for node_uid in self.node_scope:    # pylint: disable=no-member, not-an-iterable
                node, _ = self.retrieve_node(node_uid)    # pylint: disable=no-member
                if node:
                    node_uids = map(lambda node: node.uid, node.tree_front_walker())
                    if self.member_cls.valid_objects.filter(user=user, owner__uid__in=node_uids).exists():    # pylint: disable=no-member
                        return True
        return False

    def is_visible_to_employee(self, user):
        '''
        TODO
        对user是否可见，由自身以及下级是否开放决定
        '''
        return self.is_open_to_employee(user)

    def is_open_to_manager(self, user):
        '''
        对管理员是否开放，由用户所在管理员组决定
        '''
        return self.under_manage(user)

    def is_visible_to_manager(self, user):
        '''
        由自身以及下级是否在管理范围内决定
        '''
        if self.is_open_to_manager(user):
            return True

        manage_node_uids = user.manage_node_uids

        if set(self.upstream_uids) & manage_node_uids:
            return True

        for node in self.retrieve_nodes(manage_node_uids):
            if self.node_uid in set(node.upstream_uids):
                return True

        return False

    def refresh_visibility_scope(self):
        '''
        更新可见范围
        '''

        old_node_scope = set(self.node_scope)
        old_user_scope = set(self.user_scope)

        valid_node_scope = set(node.node_uid for node in self.retrieve_nodes(old_node_scope))

        from oneid_meta.models import User
        valid_user_scope = set(user.username for user in User.get_from_pks(old_user_scope, pk_name='username'))

        if valid_node_scope != old_node_scope:
            self.node_scope = list(valid_node_scope)
            self.save(update_fields=['node_scope'])

        if valid_user_scope != old_user_scope:
            self.user_scope = list(valid_user_scope)
            self.save(update_fields=['user_scope'])


class TreeNode():
    '''
    Tree feature
    '''
    uid = ''
    objects = None
    parent = None
    NODE_PREFIX = ''

    def tree_front_walker(self):
        '''
        前序遍历
        '''
        yield self
        for child in self.children:
            for node in child.tree_front_walker():
                yield node

    @property
    def children(self):
        '''
        子节点
        '''
        raise NotImplementedError

    @property
    def node_uid(self):
        '''
        节点UID，在部门和组范围内唯一
        '''
        return self.NODE_PREFIX + self.uid

    @property
    def parent_uid(self):
        '''
        父级部门或组id
        '''
        return self.parent.uid if self.parent else None    # pylint: disable=no-member

    @property
    def parent_node_uid(self):
        '''
        父级节点id
        '''
        return (self.NODE_PREFIX + self.parent_uid) if self.parent_uid is not None else None

    @property
    def is_org(self):
        return self.parent_uid == 'root'

    @property
    def is_group(self):
        from oneid_meta.models import Group

        return self.NODE_PREFIX == Group.NODE_PREFIX

    @property
    def is_dept(self):
        from oneid_meta.models import Dept

        return self.NODE_PREFIX == Dept.NODE_PREFIX

    @property
    def is_org_dept(self):
        from oneid_meta.models import Org
        return Org.valid_objects.filter(dept=self).exists()

    @property
    def is_org_group(self):
        from oneid_meta.models import Org
        return Org.valid_objects.filter(group=self).exists()

    @property
    def is_org_direct(self):
        from oneid_meta.models import Org
        return Org.valid_objects.filter(direct=self).exists()

    @property
    def is_org_manager(self):
        from oneid_meta.models import Org
        return Org.valid_objects.filter(manager=self).exists()

    @property
    def is_org_role(self):
        from oneid_meta.models import Org
        return Org.valid_objects.filter(role=self).exists()

    @property
    def is_org_label(self):
        from oneid_meta.models import Org
        return Org.valid_objects.filter(label=self).exists()

    @property
    def org(self):
        '''
        所属组织
        '''
        from oneid_meta.models import Org
        if self.is_root:
            return None
        elif not self.is_org:
            return self.parent.org
        elif self.is_group:
            return Org.valid_objects.filter(group=self).first()
        elif self.is_dept:
            return Org.valid_objects.filter(dept=self).first()
        return None

    @property
    def parent_name(self):
        '''
        父级节点名称
        '''
        return self.parent.name if self.parent else None    # pylint: disable=no-member

    def path_up_to(self, top=None):
        '''
        节点向上追溯的路径，包括该节点本身，包括终点节点
        '''
        if top is None:
            top = self.__class__.objects.get(uid='root')

        node = self

        while node and node.uid != top.uid and node.uid != 'root':
            yield node
            node = node.parent

        yield node

    @property
    def upstream_uids(self):
        '''
        节点向上追溯的路径，包括该节点本身，包括终点节点，以node_uid形式返回
        '''
        key = f'oneid:node:{self.node_uid}:upstream'
        res = cache.get(key)
        if res is None:
            uids = [node.node_uid for node in self.path_up_to()]
            cache.set(key, uids[1:])
            return uids

        return chain([self.node_uid], res)

    @property
    def downstream_uids(self):
        '''
        节点以及其子孙节点，以node_uid形式返回
        目前使用频次不大
        '''
        for node in self.downstream:
            yield node.node_uid

    @property
    def downstream(self):
        '''
        节点以及其子孙节点，以object形式返回
        '''
        yield self
        for node in self.children:
            yield from node.downstream

    def update_cache(self):
        '''
        更新缓存
        '''
        cache.delete(f'oneid:node:{self.node_uid}:upstream')
        _ = self.upstream_uids

    @staticmethod
    def retrieve_node(node_uid):
        '''
        通过node_uid 获取node及该节点类型
        '''
        from oneid_meta.models import Dept, Group
        if node_uid.startswith(Dept.NODE_PREFIX):
            uid = node_uid.replace(Dept.NODE_PREFIX, '', 1)
            return Dept.valid_objects.filter(uid=uid).first(), 'dept'
        if node_uid.startswith(Group.NODE_PREFIX):
            uid = node_uid.replace(Group.NODE_PREFIX, '', 1)
            return Group.valid_objects.filter(uid=uid).first(), 'group'
        return None, ''

    @staticmethod
    def retrieve_nodes(node_uids):
        '''
        通过node_uids 批量获取node
        '''
        from oneid_meta.models import Dept, Group
        dept_uids = set()
        group_uids = set()
        for node_uid in node_uids:
            if node_uid.startswith(Dept.NODE_PREFIX):
                dept_uids.add(node_uid.replace(Dept.NODE_PREFIX, '', 1))
            elif node_uid.startswith(Group.NODE_PREFIX):
                group_uids.add(node_uid.replace(Group.NODE_PREFIX, '', 1))
        for node in Dept.valid_objects.filter(uid__in=dept_uids):
            yield node
        for node in Group.valid_objects.filter(uid__in=group_uids):
            yield node

    @property
    def member_cls(self):
        '''
        成员关系类型
        '''
        raise NotImplementedError

    @property
    def owner_perm_cls(self):
        '''
        权限结果类型
        '''
        raise NotImplementedError

    def under_manage(self, user):
        '''
        判断是否在某人管理之下
        '''
        if user.is_admin:
            return True
        upstream_uids = set(self.upstream_uids)

        org = self.org
        if not org:
            return False
        for manager_group in user.org_manager_groups(org):
            if manager_group.scope_subject == 2:    # 指定节点、人
                if upstream_uids & set(manager_group.nodes):
                    return True
            if manager_group.scope_subject == 1:    # 所在节点
                if upstream_uids & set(user.node_uids):
                    return True
        return False

    @property
    def detail_serializer_cls(self):
        '''
        详情序列化类
        TODO: 不再使用
        '''
        raise NotImplementedError

    @property
    def detail_serializer(self):
        '''
        详情序列化实例
        TODO: 不再使用
        '''
        raise NotImplementedError
