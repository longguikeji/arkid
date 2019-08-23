'''
views about user
- UserList
- UserDetail
- UserGroup
- UserDept
'''

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
)
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from oneid_meta.models import User, Group, Dept
from oneid.permissions import (
    IsAdminUser,
    IsUserManager,
    UserEmployeeReadable,
    UserManagerReadable,
    CustomPerm,
)
from siteapi.v1.serializers.user import UserSerializer, EmployeeSerializer
from siteapi.v1.serializers.group import GroupListSerializer, GroupSerializer
from siteapi.v1.serializers.dept import DeptListSerializer, DeptSerializer
from common.django.drf.paginator import DefaultListPaginator
from executer.core import CLI
from executer.utils import operation


class UserListCreateAPIView(generics.ListCreateAPIView):
    '''
    用户列表 [GET],[POST]
    '''
    serializer_class = EmployeeSerializer
    pagination_class = DefaultListPaginator

    read_permission_classes = [IsAuthenticated & IsAdminUser]
    write_permission_classes = [IsAuthenticated & (IsAdminUser | CustomPerm('system_user_create'))]

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            return [perm() for perm in self.read_permission_classes]
        return [perm() for perm in self.write_permission_classes]

    def get_queryset(self):
        '''
        return queryset for list [GET]
        '''
        kwargs = {}
        queryset = User.valid_objects.filter(**kwargs).exclude(is_boss=True).exclude(username='admin').order_by('id')

        return queryset

    @transaction.atomic()
    def create(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        create user [POST]
        '''
        data = request.data
        user_info = data.get('user', '')

        group_uids = []
        dept_uids = []

        node_uids = data.get('node_uids', [])
        if node_uids:
            for node_uid in node_uids:
                if node_uid.startswith(Dept.NODE_PREFIX):
                    dept_uids.append(node_uid.replace(Dept.NODE_PREFIX, '', 1))
                elif node_uid.startswith(Group.NODE_PREFIX):
                    group_uids.append(node_uid.replace(
                        Group.NODE_PREFIX,
                        '',
                    ))
        else:
            group_uids = data.get('group_uids', [])
            dept_uids = data.get('dept_uids', [])

        user_info.pop('password', None)
        user = CLI().create_user(user_info)
        user.origin = 1    # 管理员添加
        user.save()

        self.assign_user(user, dept_uids=dept_uids, group_uids=group_uids)

        user_serializer = EmployeeSerializer(user)
        return Response(user_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(user_serializer.data))

    def assign_user(self, user, dept_uids, group_uids):
        '''
        - add_user_to_depts
        - add_user_to_groups
        :param User user:
        :param list dept_uids: list of uid
        :param list group_uids: list of uid
        '''
        depts = []
        for dept_uid in dept_uids:
            try:
                dept = Dept.valid_objects.get(uid=dept_uid)
            except ObjectDoesNotExist:
                raise ValidationError({'dept_uids': ['dept:{} does not exist'.format(dept_uid)]})
            depts.append(dept)

        groups = []
        for group_uid in group_uids:
            try:
                group = Group.valid_objects.get(uid=group_uid)
            except ObjectDoesNotExist:
                raise ValidationError({'group_uids': ['group:{} does not exist'.format(group_uid)]})
            groups.append(group)

        cli = CLI()
        cli.add_user_to_depts(user, depts)
        cli.add_user_to_groups(user, groups)


class UserIsolatedAPIView(generics.ListAPIView):
    '''
    独立用户列表
    '''
    serializer_class = UserSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        kwargs = {}
        queryset = User.isolated_objects.filter(**kwargs).order_by()
        return queryset


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    特定用户信息 [GET],[PATCH],[DELETE]
    '''
    serializer_class = EmployeeSerializer

    read_permission_classes = [IsAuthenticated & (UserManagerReadable | IsAdminUser)]
    write_permission_classess = [IsAuthenticated & (IsUserManager | IsAdminUser)]

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            permission_classes = self.read_permission_classes
        else:
            permission_classes = self.write_permission_classess
        return [perm() for perm in permission_classes]

    def get_object(self):
        '''
        find user
        :rtype: oneid_meta.models.User
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        try:
            self.check_object_permissions(self.request, user)
        except PermissionDenied:
            raise NotFound
        return user

    def retrieve(self, request, *args, **kwargs):
        '''
        return user detail [GET]
        '''
        user = self.get_object()
        return Response(EmployeeSerializer(user).data)

    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        update user detail [PATCH]
        '''
        user = self.get_object()
        data = request.data
        data.pop('password', None)
        user = CLI().update_user(user, data)
        user_serializer = EmployeeSerializer(user)
        return Response(user_serializer.data)

    def delete(self, request, *args, **kwargs):
        '''
        delete user [DELETE]
        '''
        user = self.get_object()
        CLI().delete_users([user])
        return Response(status=status.HTTP_204_NO_CONTENT)


class UcenterUserDetailAPIView(generics.RetrieveAPIView):
    '''
    普通用户身份查看他人信息 [GET]
    '''

    permission_classes = [IsAuthenticated & UserEmployeeReadable]

    serializer_class = UserSerializer

    def get_object(self):
        '''
        find user
        :rtype: oneid_meta.models.User
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        try:
            self.check_object_permissions(self.request, user)
        except PermissionDenied:
            raise NotFound

        return user


class UserGroupView(generics.RetrieveUpdateAPIView):
    '''
    用户所属组信息 [GET],[PATCH]
    TODO: 交叉验证
    '''
    read_permission_classes = [IsAuthenticated & (UserManagerReadable | IsAdminUser)]
    write_permission_classess = [IsAuthenticated & (IsUserManager | IsAdminUser)]

    serializer_class = GroupListSerializer

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            permission_classes = self.read_permission_classes
        else:
            permission_classes = self.write_permission_classess
        return [perm() for perm in permission_classes]

    def get_object(self):
        '''
        find user
        :rtype: oneid_meta.models.User
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        try:
            self.check_object_permissions(self.request, user)
        except PermissionDenied:
            raise NotFound
        return user

    @transaction.atomic()
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        update user groups
        '''
        user = self.get_object()
        data = request.data
        uids = data.get('group_uids', [])
        subject = data.get('subject', '')
        update_user_nodes(request, user, nodes=[], uids=uids, node_type='group', action_subject=subject)
        return Response(GroupListSerializer(self.get_object()).data)


class UserDeptView(generics.RetrieveUpdateAPIView):
    '''
    用户所部门属信息 [GET],[PATCH]
    TODO: 交叉验证
    '''
    serializer_class = DeptListSerializer

    read_permission_classes = [IsAuthenticated & (UserManagerReadable | IsAdminUser)]
    write_permission_classess = [IsAuthenticated & (IsUserManager | IsAdminUser)]

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            permission_classes = self.read_permission_classes
        else:
            permission_classes = self.write_permission_classess
        return [perm() for perm in permission_classes]

    def get_object(self):
        '''
        find user
        :rtype: oneid_meta.models.User
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        return user

    @transaction.atomic()
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        update user depts
        '''
        user = self.get_object()
        data = request.data
        uids = data.get('dept_uids', [])
        subject = data.get('subject', '')
        update_user_nodes(request, user, nodes=[], uids=uids, node_type='dept', action_subject=subject)
        return Response(DeptListSerializer(self.get_object()).data)


class UserNodeView(generics.RetrieveUpdateAPIView):
    '''
    用户所属节点信息 [GET],[PATCH]
    TODO: 交叉验证
    '''

    read_permission_classes = [IsAuthenticated & (UserManagerReadable | IsAdminUser)]
    write_permission_classess = [IsAuthenticated & (IsUserManager | IsAdminUser)]

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            permission_classes = self.read_permission_classes
        else:
            permission_classes = self.write_permission_classess
        return [perm() for perm in permission_classes]

    def get_object(self):
        '''
        find user
        :rtype: oneid_meta.models.User
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        try:
            self.check_object_permissions(self.request, user)
        except PermissionDenied:
            raise NotFound
        return user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        data = DeptSerializer(user.depts, many=True).data + \
            GroupSerializer(user.groups, many=True).data
        return Response({'nodes': data})

    @transaction.atomic()
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        user = self.get_object()
        node_uids = request.data.get('node_uids', [])
        subject = request.data.get('subject', [])
        group_uids = []
        dept_uids = []
        for node_uid in node_uids:
            if node_uid.startswith(Group.NODE_PREFIX):
                group_uids.append(node_uid.replace(Group.NODE_PREFIX, '', 1))
            elif node_uid.startswith(Dept.NODE_PREFIX):
                dept_uids.append(node_uid.replace(Dept.NODE_PREFIX, '', 1))
        update_user_nodes(request, user, nodes=[], uids=group_uids, node_type='group', action_subject=subject)
        update_user_nodes(request, user, nodes=[], uids=dept_uids, node_type='dept', action_subject=subject)
        return self.get(request)


def update_user_nodes(request, user, nodes, uids, node_type, action_subject):
    '''
    :param oneid_meta.groups.User user:
    :param list nodes:
    :param list uids: 优先级低于`nodes`
    :param str node_type: group or dept
    :param str action_subject: enum(['add', 'delete', 'override'])
    '''
    if action_subject not in ('add', 'delete', 'override'):
        raise ValidationError({'subject': ['this field must be one of add, delete, override']})

    if not nodes:
        nodes = []
        if node_type.lower() == 'dept':
            cls = Dept
        elif node_type.lower() == 'group':
            cls = Group
        else:
            raise ValueError(f'invalid node_type: {node_type}')

        for uid in uids:
            try:
                node = cls.valid_objects.get(uid=uid)
                nodes.append(node)
            except ObjectDoesNotExist:
                raise ValidationError({'node_uids': ['node:{} does not exist'.format(uid)]})

    cli = CLI()
    if action_subject == 'add':
        func = getattr(cli, 'add_user_to_{}s'.format(node_type))
        func(user, nodes)
    elif action_subject == 'delete':
        func = getattr(cli, 'delete_user_from_{}s'.format(node_type))
        func(user, nodes)
    elif action_subject == 'override':
        diff = operation.list_diff(nodes, getattr(user, '{}s'.format(node_type)))
        add_nodes = diff['>']
        delete_nodes = diff['<']
        add_func = getattr(cli, 'add_user_to_{}s'.format(node_type))
        add_func(user, add_nodes)
        delete_func = getattr(cli, 'delete_user_from_{}s'.format(node_type))
        delete_func(user, delete_nodes)
