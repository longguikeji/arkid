'''
views about user
- UserList
- UserDetail
- UserGroup
- UserDept
'''
# pylint: disable=too-many-lines
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
)
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from oneid_meta.models import User, Group, Dept, GroupMember, UserPerm
from oneid.permissions import (
    IsAdminUser,
    IsManagerUser,
    IsUserManager,
    UserEmployeeReadable,
    UserManagerReadable,
    CustomPerm,
)
from siteapi.v1.serializers.user import UserSerializer, EmployeeSerializer, ResetUserPasswordSerializer
from siteapi.v1.serializers.group import GroupListSerializer, GroupSerializer
from siteapi.v1.serializers.dept import DeptListSerializer, DeptSerializer
from common.django.drf.paginator import DefaultListPaginator
from executer.core import CLI
from executer.utils import operation
from tasksapp.tasks import update_users_cache


class UserListCreateAPIView(generics.ListCreateAPIView):
    '''
    用户列表 [GET],[POST]
    :GET
    - 主管理员可见全部
    - 子管理员可见管理范围内的指定人、指定节点及其子孙节点内的所有人
    :POST
    - 主管理员可以创建用户
    - 拥有 system_user_create 权限的子管理员
    '''
    serializer_class = EmployeeSerializer
    pagination_class = DefaultListPaginator

    read_permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]
    write_permission_classes = [IsAuthenticated & (IsAdminUser | CustomPerm('system_user_create'))]

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            return [perm() for perm in self.read_permission_classes]
        return [perm() for perm in self.write_permission_classes]

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def get_queryset(self):
        '''
        return queryset for list [GET]
        '''
        queryset = User.valid_objects.all()
        keyword = self.request.query_params.get('keyword', '')
        if keyword != '':
            queryset = queryset.filter(Q(username__icontains=keyword) | Q(email__icontains=keyword) | \
                                       Q(private_email__icontains=keyword) | Q(mobile__icontains=keyword) | Q(
                name__icontains=keyword)). \
                exclude(is_boss=True).exclude(username='admin').order_by('id')
        else:
            queryset = queryset.exclude(is_boss=True).exclude(username='admin').order_by('id')

        # 支持通过 user_id 搜索
        # QueryString 中格式为 '&user_ids=id1 ... idn'
        user_ids = self._get_user_ids(self.request.query_params.get('user_ids', ''), 'user')
        queryset = queryset.filter(pk__in=user_ids) if user_ids is not None else queryset

        # 支持通过 usernames 搜索
        # QueryString 中格式为 '&usernames=username1 ... usernamen'
        usernames = self.request.query_params.get('usernames', '')
        if usernames != '':
            usernames = usernames.split(' ')
            queryset = queryset.filter(username__in=usernames)

        # 支持通过 group_uid 搜索 (保留属于group_uids[]的用户)
        # QueryString 中格式为 '&group_uids=uid1 ... uidn'
        user_ids = self._get_user_ids(self.request.query_params.get('group_uids', ''), 'group')
        queryset = queryset.filter(pk__in=user_ids) if user_ids is not None else queryset

        # 支持通过 -group_uid 搜索 (保留不属于group_uids[]的用户)
        # QueryString 中格式为 '&group_uids=uid1 ... uidn'
        user_ids = self._get_user_ids(self.request.query_params.get('-group_uids', ''), 'group')
        queryset = queryset.exclude(pk__in=user_ids) if user_ids is not None else queryset

        # 支持通过 perm_uid 搜索 (保留拥有perm_uids[]的用户)
        # QueryString 中格式为 '&perm_uids=uid1 ... uidn'
        user_ids = self._get_user_ids(self.request.query_params.get('perm_uids', ''), 'perm')
        queryset = queryset.filter(pk__in=user_ids) if user_ids is not None else queryset

        # 支持通过 -perm_uid 搜索 (保留未拥有perm_uids[]的用户)
        # QueryString 中格式为 '&perm_uids=uid1 ... uidn'
        user_ids = self._get_user_ids(self.request.query_params.get('-perm_uids', ''), 'perm')
        queryset = queryset.exclude(pk__in=user_ids) if user_ids is not None else queryset

        filter_params = (
            'wechat_unionid',
            'name',
            'name__icontains',
            'username',
            'username__icontains',
            'email',
            'email__icontains',
            'private_email',
            'private_email__icontains',
            'mobile',
            'mobile__icontains',
            'gender',
            'remark',
            'remark__icontains',
            'created__lte',
            'created__gte',
            'last_active_time__lte',
            'last_active_time__gte',
            'unbound_wechat',
            'unbound_ding',
            'unbound_alipay',
            'unbound_qq',
        )
        mapper = {
            'wechat_unionid': 'wechat_user__unionid',
            'unbound_wechat': 'wechat_user__isnull',
            'unbound_ding': 'ding_user__isnull',
            'unbound_alipay': 'alipay_user__isnull',
            'unbound_qq': 'qq_user__isnull',
        }
        boolean_params = (
            'unbound_wechat',
            'unbound_ding',
            'unbound_alipay',
            'unbound_qq',
        )
        _boolean_map = {
            'true': True,
            'false': False,
        }

        for param in filter_params:
            value = self.request.query_params.get(param, None)
            # 用户关联账号相关搜索
            if value is not None and param in boolean_params and value.lower() in _boolean_map.keys():
                param = mapper.get(param)
                queryset = queryset.filter(**{param: _boolean_map.get(value.lower())})
                continue
            if value is not None:
                param = mapper.get(param, param)
                queryset = queryset.filter(**{param: value})

        # 获取 query string 中自定义字段（*__custom）
        # 支持 *__(lte, gte, lt, gt 等)__custom 形式,需进行范围搜索的字段在存储时保证传入的为string
        suffixes = ['__lte__custom', '__lt__custom', '__gte__custom', '__gt__custom', '__custom']
        for key, value in self.request.query_params.items():
            for suffix in suffixes:
                if key.endswith(suffix):
                    _key = 'custom_user__data__"{custom_field}"{suffix}'.format(custom_field=key[:-1 * len(suffix)],
                                                                                suffix=suffix[:-8])
                    queryset = queryset.filter(**{_key: value})
                    break
        # 支持自定义排序
        # QueryString 中格式为 '&sort=field1 ... fieldn'
        _sort = self.request.query_params.get('sort')
        _sort = _sort.split(' ') if _sort else []
        # 校验排序字段合法性
        for field_name in _sort:
            field_name = field_name[1:] if field_name.startswith('-') else field_name
            try:
                # pylint: disable=no-member
                # pylint: disable=protected-access
                _ = User._meta.get_field(field_name)
            except FieldDoesNotExist:
                raise ValidationError({'sort': f"Invalid order_by argument: '{field_name}'"})
        queryset = queryset.order_by(*_sort)

        user = self.request.user
        if user.is_admin:
            return queryset.select_related('wechat_user', 'custom_user', 'ding_user')

        under_manage_user_ids = set()

        for item in queryset:    # 这种遍历不能接受
            if item.is_visible_to_manager(user):
                under_manage_user_ids.add(item.username)

        under_manage_user_query_set = queryset.filter(username__in=under_manage_user_ids)
        return under_manage_user_query_set

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

        cli = CLI()
        password = user_info.pop('password', None)
        user = cli.create_user(user_info)
        if password:
            validate_password(password)
            cli.set_user_password(user, password)
        user.origin = 1    # 管理员添加
        user.save()

        self.assign_user(user, dept_uids=dept_uids, group_uids=group_uids)

        user_serializer = EmployeeSerializer(user)
        return Response(user_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(user_serializer.data))

    @staticmethod
    def assign_user(user, dept_uids, group_uids):
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

    def _get_user_ids(self, uids, subject):
        """
        获取即将过滤的 user_ids 列表
        :param uids: 通过 QueryString 获取的 uids
        :param subject: 搜索的标签类型
        """
        if uids == '':
            return None
        user_ids = None
        uids = uids.split(' ')
        if subject == 'group':
            user_ids = GroupMember.valid_objects. \
                filter(owner__uid__in=uids). \
                values('user__id'). \
                distinct()
        if subject == 'perm':
            user_perms = UserPerm.valid_objects.filter(perm__uid__in=uids)
            for user_perm in user_perms:    # 校验权限是否在管辖范围之内
                if not user_perm.owner.under_manage(self.request.user):
                    raise PermissionDenied({'perm_uids': f"Invalid perm_uids argument: '{user_perm.perm.uid}'"})
            user_ids = user_perms.filter(value=True).values('owner__id').distinct()
        if subject == 'user':
            user_ids = uids
        return user_ids


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

    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        update user detail [PATCH]
        '''
        user = self.get_object()
        data = request.data
        user = CLI().update_user(user, data)
        return Response(UserSerializer(user).data)

    def delete(self, request, *args, **kwargs):
        '''
        delete user [DELETE]
        '''
        user = self.get_object()
        CLI().delete_users([user])
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPasswordAPIView(generics.UpdateAPIView):
    '''
    修改用户密码
    修改他人密码要求主管理员权限，即使对此人有管理权限的子管理员也不能修改
    '''

    serializer_class = ResetUserPasswordSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def get_object(self):
        '''
        find user
        :rtype: oneid_meta.models.User
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        return user


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
        update_user_nodes(user, nodes=[], uids=uids, node_type='group', action_subject=subject)
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
        update_user_nodes(user, nodes=[], uids=uids, node_type='dept', action_subject=subject)
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
        with transaction.atomic():
            update_user_nodes(user, nodes=[], uids=group_uids, node_type='group', action_subject=subject)
            update_user_nodes(user, nodes=[], uids=dept_uids, node_type='dept', action_subject=subject)
            # 可重复读事务提交后，更新缓存数据至最新版本
            transaction.on_commit(lambda: update_users_cache.delay([user.username]))
        return self.get(request)


def update_user_nodes(user, nodes, uids, node_type, action_subject):    # pylint: disable=too-many-locals
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
        if (node_type == 'group') & (not user.is_intra):
            # 由于 `extern` 对外隐藏而又必须存在，在覆盖时常不会提供
            # 故对没有显示说要从 `extern` 移除的，视为不移除
            extern_group, _ = Group.valid_objects.get_or_create(uid='extern')
            nodes.append(extern_group)
        diff = operation.list_diff(nodes, getattr(user, '{}s'.format(node_type)))
        add_nodes = diff['>']
        delete_nodes = diff['<']
        add_func = getattr(cli, 'add_user_to_{}s'.format(node_type))
        add_func(user, add_nodes)
        delete_func = getattr(cli, 'delete_user_from_{}s'.format(node_type))
        delete_func(user, delete_nodes)


class UserIntra2ExternView(views.APIView):
    '''
    内部用户转化为外部用户 [PATCH]
    '''

    permission_classes = [IsAuthenticated & IsAdminUser]

    write_serializer_class = UserSerializer
    read_serializer_class = EmployeeSerializer

    def get_object(self):
        '''
        must be intra
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound

        if not user.is_intra:
            raise ValidationError({'user': 'must be intra'})

        return user

    def patch(self, request, username):    # pylint: disable=unused-argument
        '''
        [PATCH]
        '''
        user = self.get_object()
        serializer = self.write_serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.intra_to_extern(user)
        return Response(self.read_serializer_class(user).data)

    @staticmethod
    def intra_to_extern(user):
        '''
        内部用户转化为外部用户
        '''
        cli = CLI()
        cli.delete_user_from_depts(user, user.depts)
        cli.delete_user_from_groups(user, user.groups)
        cli.add_user_to_groups(user, Group.valid_objects.filter(uid='extern'))


class UserExtern2IntraView(views.APIView):
    '''
    外部用户转化为内部用户 [PATCH]
    '''

    permission_classes = [IsAuthenticated & IsAdminUser]

    write_serializer_class = UserSerializer
    read_serializer_class = EmployeeSerializer

    def get_object(self):
        '''
        must be extern
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound

        if user.is_intra:
            raise ValidationError({'user': 'must be extern'})

        return user

    def patch(self, request, username):    # pylint: disable=unused-argument
        '''
        [PATCH]
        '''
        user = self.get_object()
        serializer = self.write_serializer_class(user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # node_uid = request.data.get('node_uid', '')
        # if not node_uid:
        #     raise ValidationError({'node_uid': 'required'})
        # node, node_type = Node.retrieve_node(node_uid)
        # if not node or node_type != 'dept':
        #     raise ValidationError({'node_uid': 'invalid'})
        self.extern_to_intra(user)
        return Response(self.read_serializer_class(user).data)

    @staticmethod
    def extern_to_intra(user, depts=None):
        '''
        外部用户转化为内部用户
        '''

        cli = CLI()
        cli.delete_user_from_groups(user, user.groups)
        if depts:
            cli.add_user_to_depts(user, depts)
