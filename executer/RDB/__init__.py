'''
RDB数据操作
'''
# pylint: disable=import-error
# pylint: disable=no-self-use

from rest_framework.exceptions import ValidationError
from django.conf import settings
from executer.core import Executer
from executer.utils.password import encrypt_password
from oneid_meta.models import (
    Dept,
    DeptMember,
    DeptPerm,
    Group,
    GroupMember,
    GroupPerm,
    UserPerm,
    Perm,
)
from siteapi.v1.serializers.user import (
    UserSerializer,
    DingUserSerializer,
    PosixUserSerializer,
)
from siteapi.v1.serializers.dept import (
    DeptDetailSerializer, )

from siteapi.v1.serializers.group import (
    GroupDetailSerializer, )


class RDBExecuter(Executer):    # pylint: disable=abstract-method
    '''
    RDB数据操作接口
    '''
    def create_user(self, user_info):
        '''
        创建用户
        :param dict user_info:
        '''
        serializer = UserSerializer(data=user_info)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        for perm in Perm.valid_objects.all():
            UserPerm.valid_objects.create(owner=serializer.instance, perm=perm)
        return serializer.instance

    def update_user(self, user, user_info):
        '''
        更新用户
        '''
        user_serializer = UserSerializer(user, data=user_info, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return user_serializer.instance

    def set_user_password(self, user, plaintext):
        '''
        设置用户密码
        '''
        user.password = encrypt_password(plaintext, encryption=settings.PASSWORD_ENCRYPTION)
        user.save()

    def delete_users(self, users):
        """
        delete redundant users
        """
        for user in users:
            for dept_member in DeptMember.objects.filter(user=user):
                dept_member.kill()

            for group_member in GroupMember.objects.filter(user=user):
                group_member.kill()

            for user_perm in UserPerm.objects.filter(owner=user):
                user_perm.kill()
            user.delete()

    def add_users_to_dept(self, users, dept):
        '''
        将一批用户加入一个部门
        :param list users:
        :param oneid_meta.models.Dept dept:
        '''
        max_order_no = DeptMember.get_max_order_no(owner=dept)
        order_no = max_order_no

        for user in users:
            if not DeptMember.valid_objects.filter(user=user, owner=dept).exists():
                order_no += 1
                DeptMember.valid_objects.create(user=user, owner=dept, order_no=order_no)

    def add_users_to_group(self, users, group):
        '''
        将一批用户添加至一个组
        :param list users:
        :param oneid_meta.models.group group:
        '''
        max_order_no = GroupMember.get_max_order_no(owner=group)
        order_no = max_order_no
        for user in users:
            if not GroupMember.valid_objects.filter(user=user, owner=group).exists():
                order_no += 1
                GroupMember.valid_objects.create(user=user, owner=group, order_no=order_no)

    def add_user_to_depts(self, user, depts):
        '''
        将一个用户加入一批部门
        :param oneid_meta.models.User user:
        :param list depts:
        '''
        for dept in depts:
            if not DeptMember.valid_objects.filter(user=user, owner=dept).exists():
                order_no = DeptMember.get_max_order_no(owner=dept) + 1
                DeptMember.valid_objects.create(user=user, owner=dept, order_no=order_no)

    def add_user_to_groups(self, user, groups):
        '''
        将一个用户加入一批组
        :param oneid_meta.models.User user:
        :param list groups:
        '''
        for group in groups:
            if not GroupMember.valid_objects.filter(user=user, owner=group).exists():
                order_no = GroupMember.get_max_order_no(owner=group) + 1
                GroupMember.valid_objects.create(user=user, owner=group, order_no=order_no)

    def delete_user_from_depts(self, user, depts):
        '''
        将一个用户从一批部门中移除
        '''
        for dept in depts:
            target = DeptMember.valid_objects.filter(user=user, owner=dept).first()
            if target:
                target.kill()

    def delete_user_from_groups(self, user, groups):
        '''
        将一个用户从一批组中移除
        '''
        for group in groups:
            target = GroupMember.valid_objects.filter(user=user, owner=group).first()
            if target:
                target.kill()

    def create_dept(self, dept_info):
        '''
        创建部门
        '''
        serializer = DeptDetailSerializer(data=dept_info)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        dept = serializer.instance

        dept.order_no = Dept.get_max_order_no(parent=dept.parent) + 1
        dept.save()

        # 批量创建组权限
        #  1) 去重
        perm_ids = Perm.valid_objects.values_list('pk', flat=True)
        exist_perm_ids = DeptPerm.valid_objects.filter(owner=serializer.instance).values_list('perm_id', flat=True)
        perm_ids = set(perm_ids).difference(exist_perm_ids)
        #  2) 批量创建
        dept_perms = [DeptPerm(owner=serializer.instance, perm_id=x) for x in perm_ids]
        DeptPerm.objects.bulk_create(dept_perms)

        return serializer.instance

    def add_dept_to_dept(self, dept, parent_dept):
        '''
        将一个新部门加入另一个部门作为后者子部门
        '''
        if dept == parent_dept or parent_dept.if_belong_to_dept(dept, recursive=True):
            raise ValidationError({'node': ['deadlock']})
        dept.parent = parent_dept
        dept.order_no = Dept.get_max_order_no(parent=parent_dept) + 1
        dept.save(update_fields=['order_no', 'parent'])

    def create_group(self, group_info):
        '''
        创建组
        '''
        serializer = GroupDetailSerializer(data=group_info)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        group = serializer.instance

        group.order_no = Group.get_max_order_no(parent=group.parent) + 1
        group.save()

        # 批量创建组权限
        #  1) 去重
        perm_ids = Perm.valid_objects.values_list('pk', flat=True)
        exist_perm_ids = GroupPerm.valid_objects.filter(owner=serializer.instance).values_list('perm_id', flat=True)
        perm_ids = set(perm_ids).difference(exist_perm_ids)
        #  2) 批量创建
        group_perms = [GroupPerm(owner=serializer.instance, perm_id=x) for x in perm_ids]
        GroupPerm.objects.bulk_create(group_perms)

        return serializer.instance

    def add_group_to_group(self, group, parent_group):
        '''
        将一个新组加入另一个组作为后者子组
        '''
        if group == parent_group or parent_group.if_belong_to_group(group, recursive=True):
            raise ValidationError({'node': ['deadlock']})
        group.parent = parent_group
        if parent_group.uid == 'intra':
            group.top = group.uid
        else:
            group.top = parent_group.top
        group.order_no = Group.get_max_order_no(parent=parent_group) + 1
        group.save(update_fields=['order_no', 'parent', 'top'])

    def sort_users_in_dept(self, users, dept):
        '''
        调整一批人在部门中的排序
        '''
        dept_members = [DeptMember.valid_objects.get(user=user, owner=dept) for user in users]
        DeptMember.sort_as(dept_members)

    def sort_users_in_group(self, users, group):
        '''
        调整一批人在组中的排序
        '''
        group_members = [GroupMember.valid_objects.get(user=user, owner=group) for user in users]
        GroupMember.sort_as(group_members)

    def sort_depts_in_dept(self, depts, parent_dept):
        '''
        调整一批部门在父部门中的排序
        '''
        for dept in depts:
            if dept.parent != parent_dept:
                raise ValidationError({'node': ['unrelated']})
        Dept.sort_as(depts)

    def sort_groups_in_group(self, groups, parent_group):
        '''
        调整一批组在父组中的排序
        '''
        for group in groups:
            if group.parent != parent_group:
                raise ValidationError({'node': ['unrelated']})
        Group.sort_as(groups)

    def delete_users_from_dept(self, users, dept):
        '''
        将一批人从部门中删除
        '''
        for user in users:
            target = DeptMember.valid_objects.filter(owner=dept, user=user).first()
            if target:
                target.kill()

    def delete_users_from_group(self, users, group):
        '''
        将一批人从组中删除
        '''
        for user in users:
            target = GroupMember.valid_objects.filter(owner=group, user=user).first()
            if target:
                target.kill()

    def update_dept(self, dept, dept_info):
        '''
        更新部门信息
        '''
        serializer = DeptDetailSerializer(dept, data=dept_info, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.instance

    def update_group(self, group, group_info):
        '''
        更新组信息
        '''
        serializer = GroupDetailSerializer(group, data=group_info, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.instance

    def delete_group(self, group):
        '''
        删除组
        '''
        if group.groups:
            raise ValidationError({'node': ['protected_by_child_node']})
        if group.users:
            raise ValidationError({'node': ['protected_by_child_user']})

        for group_perm in GroupPerm.valid_objects.filter(owner=group):
            group_perm.kill()

        group.delete()

    def delete_dept(self, dept):
        '''
        删除部门
        '''
        if dept.depts:
            raise ValidationError({'node': ['protected_by_child_node']})
        if dept.users:
            raise ValidationError({'node': ['protected_by_child_user']})

        for dept_perm in DeptPerm.valid_objects.filter(owner=dept):
            dept_perm.kill()

        dept.delete()

    def move_dept_to_dept(self, dept, parent_dept):
        '''
        将一个已有部门移至另一部门下
        '''
        if dept == parent_dept or parent_dept.if_belong_to_dept(dept, recursive=True):
            raise ValidationError({'node': ['deadlock']})
        dept.order_no = Dept.get_max_order_no(parent=parent_dept) + 1
        dept.parent = parent_dept
        dept.save(update_fields=['order_no', 'parent'])

    def move_group_to_group(self, group, parent_group):
        '''
        将一个已有组移至另一组下
        '''
        if group == parent_group or parent_group.if_belong_to_group(group, recursive=True):
            raise ValidationError({'node': ['deadlock']})
        if parent_group.top != 'root' and group.top != parent_group.top:
            raise ValidationError({'node': ["across_scope"]})
        group.order_no = Group.get_max_order_no(parent=parent_group) + 1
        group.parent = parent_group
        group.save(update_fields=['order_no', 'parent'])
