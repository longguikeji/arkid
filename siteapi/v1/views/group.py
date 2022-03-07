'''
views about group
- GroupTree
- GroupChildGroup
- GroupChildUser
'''
import json
import random
import string  # pylint: disable=deprecated-module
import uuid as uuid_utils

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotFound,
    ValidationError,
    PermissionDenied,
)

from oneid_meta.models import Group, GroupMember, User
from oneid.permissions import (
    CustomPerm,
    IsAdminUser,
    IsManagerUser,
    IsNodeManager,
    NodeEmployeeReadable,
    NodeManagerReadable,
)
from siteapi.v1.serializers.user import UserListSerializer, UserSerializer
from siteapi.v1.serializers.group import (
    GroupSerializer,
    GroupTreeSerializer,
    GroupListSerializer,
    GroupDetailSerializer,
    GroupWithVerboseManagerGroup,
    ManagerGroupListSerializer,
)
from siteapi.v1.views import node as node_views
from siteapi.v1.views.utils import (
    get_users_from_uids,
    update_users_of_owner,
    get_groups_from_uids,
    gen_uid,
)
from executer.core import CLI
from common.django.drf.paginator import DefaultListPaginator
from common.django.drf.views import catch_json_load_error
from webhook.manager import WebhookManager
from django.db import transaction


class GroupListAPIView(generics.ListAPIView):
    '''
    get group in list

    管理员可见
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]
    serializer_class = GroupSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        '''
        filter groups
        '''
        kwargs = {}
        name = self.request.query_params.get('name', None)
        if name:
            kwargs.update(name__icontains=name)

        return Group.valid_objects.filter(**kwargs).exclude(uid='root').order_by('id')


class GroupScopeListAPIView(generics.ListAPIView):
    '''
    指定节点下属的所有节点，包括该节点自身 [GET]

    管理员可见
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    serializer_class = GroupTreeSerializer

    def get_object(self):
        '''
        find group
        '''
        group = Group.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not group:
            raise NotFound
        return group

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        以列表形式输出指定节点下属的所有节点
        '''
        node = self.get_object()
        nodes = list(self.get_serializer(node).flat_tree())
        if nodes:
            nodes[0]['parent_uid'] = node.parent_uid
            nodes[0]['parent_node_uid'] = node.parent_node_uid
        return Response(nodes)


class GroupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    组信息 [GET] [PATCH] [DELETE]
    '''

    serializer_class = GroupDetailSerializer

    read_permission_classes = [IsAuthenticated & (NodeManagerReadable | IsAdminUser)]
    write_permission_classes = [IsAuthenticated & (IsNodeManager | IsAdminUser)]

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            return [perm() for perm in self.read_permission_classes]
        return [perm() for perm in self.write_permission_classes]

    def get_object(self):
        '''
        find group
        '''
        group = Group.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not group:
            raise NotFound
        try:
            self.check_object_permissions(self.request, group)
        except PermissionDenied as exc:
            if self.request.method in SAFE_METHODS:
                raise NotFound
            raise exc
        group.refresh_visibility_scope()
        return group

    @transaction.atomic()
    def perform_destroy(self, instance):
        '''
        删除组 [DELETE]
        '''
        if self.request.query_params.get('ignore_user', '') in ('true', 'True'):
            CLI().delete_users_from_group(instance.users, instance)
        CLI().delete_group(instance)
        transaction.on_commit(lambda: WebhookManager.group_deleted(instance))

    @catch_json_load_error
    @transaction.atomic()
    def update(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        更新组信息  [PATCH]
        '''
        group = self.get_object()
        data = json.loads(request.body.decode('utf-8'))
        group = CLI().update_group(group, data)
        transaction.on_commit(lambda: WebhookManager.group_updated(group))
        return Response(self.get_serializer(group).data)


class ManagerGroupTreeAPIView(APIView):
    '''
    管理员身份组结构树 [GET]
    '''

    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']
        node_uid = Group.NODE_PREFIX + uid
        kwargs['uid'] = node_uid
        return node_views.ManagerNodeTreeAPIView().dispatch(request, *args, **kwargs)


class UcenterGroupTreeAPIView(APIView):
    '''
    普通用户身份部门结构树 [GET]
    '''

    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']
        node_uid = Group.NODE_PREFIX + uid
        kwargs['uid'] = node_uid
        return node_views.UcenterNodeTreeAPIView().dispatch(request, *args, **kwargs)


def get_patch_scope(request):
    '''
    操作范围
    '''
    data = request.data
    group_uids = []
    node_uids = data.get('node_uids', [])
    if node_uids:
        for node_uid in node_uids:
            if node_uid.startswith(Group.NODE_PREFIX):
                group_uids.append(node_uid.replace(Group.NODE_PREFIX, '', 1))
    else:
        group_uids = data.get('group_uids', [])
    return group_uids


class GroupChildGroupAPIView(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    generics.ListCreateAPIView,
):
    '''
    组下属子组信息 [GET], [POST], [PATCH]

    管理员可见
    TODO: 权限校验需深入
    '''

    serializer_class = GroupListSerializer

    read_permission_classes = [
        IsAuthenticated & (NodeEmployeeReadable | IsAdminUser | NodeManagerReadable)
    ]
    write_permission_classes = [IsAuthenticated & (IsAdminUser | IsNodeManager)]
    create_category_permission_classes = [
        IsAuthenticated & (IsAdminUser | CustomPerm('system_category_create'))
    ]

    def dispatch(self, request, *args, **kwargs):
        '''
        管理员组下的子管理员组用专用View
        '''
        if kwargs['uid'] == 'manager' and request.method == 'GET':
            return ManagerGroupListAPIView().dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            permissions = self.read_permission_classes
        elif self.kwargs['uid'] == 'intra' and self.request.method == 'POST':  # 新建大类
            permissions = self.create_category_permission_classes
        else:
            permissions = self.write_permission_classes

        return [perm() for perm in permissions]

    def get_object(self):
        '''
        find group
        '''
        group = Group.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not group:
            raise NotFound
        self.check_object_permissions(self.request, group)
        return group

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        获取组下属子组信息 [GET]
        '''
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        添加子组,从无到有 [POST]
        '''
        parent_group = self.get_object()
        group_data = request.data
        uid = group_data.get('uid', '')
        if 'manager_group' in group_data:
            if parent_group.uid == 'manager':
                if not group_data.get('name', ''):
                    name = "".join(
                        random.choice(string.ascii_lowercase) for _ in range(8)
                    )
                    group_data.update(name=name)
            else:
                group_data.pop('manager_group')
        if not uid:
            name = group_data.get('name')
            if not name:
                raise ValidationError({'name': ['this field is required']})
            uid = gen_uid(name=name, cls=Group)
            group_data['uid'] = uid

        cli = CLI()
        group_data.update(parent_uid=self.kwargs['uid'])
        child_group = cli.create_group(group_data)
        cli.add_group_to_group(child_group, parent_group)

        if parent_group.uid == 'intra':
            self._auto_create_manager_group(request, child_group)
        transaction.on_commit(lambda: WebhookManager.group_created(child_group))
        return Response(
            GroupDetailSerializer(child_group).data, status=status.HTTP_201_CREATED
        )

    @catch_json_load_error
    def patch(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        调整子组 [PATCH]
        操作包括
        - 排序sort
        - 移动add, 即修改父部门。从无到有的添加，由create负责
        '''
        parent_group = self.get_object()
        data = json.loads(request.body.decode('utf-8'))
        subject = data.get('subject', '')
        if subject not in ['sort', 'add']:
            raise ValidationError({'subject': ['this field must be `sort` or `add`']})

        filters = {}
        if subject == 'sort':
            filters = {'parent': parent_group}

        group_uids = get_patch_scope(request)

        try:
            groups = Group.get_from_pks(
                pks=group_uids, pk_name='uid', raise_exception=True, **filters
            )
        except ObjectDoesNotExist as error:
            bad_uid = error.args[0]
            raise ValidationError({'group_uids': ['group:{} invalid'.format(bad_uid)]})

        cli = CLI()
        if subject == 'sort':
            cli.sort_groups_in_group(groups, parent_group)
        elif subject == 'add':
            for group in groups:
                cli.move_group_to_group(group, parent_group)
        return Response(GroupListSerializer(parent_group).data)

    @staticmethod
    def _auto_create_manager_group(request, child_group):
        '''
        当创建大类时，自动创建子管理员组
        成员只有创建者一人，节点范围仅此大类，人员管理范围仅自己，应用管理范围为空
        '''
        cli = CLI()
        data = {
            'uid': gen_uid(name=uuid_utils.uuid4().hex[:6], cls=Group),
            'name': f'管理分组{child_group.name}',
            'manager_group': {
                'nodes': [child_group.node_uid],
                'users': [request.user.username],
                'scope_subject': 2,
            },
        }
        manager_group = cli.create_group(data)
        parent, _ = Group.valid_objects.get_or_create(uid='manager')
        cli.add_group_to_group(manager_group, parent)
        cli.add_users_to_group([request.user], manager_group)


class ManagerGroupListAPIView(generics.RetrieveAPIView):
    '''
    get manager group in list
    '''

    permission_classes = [IsAuthenticated & IsAdminUser]

    serializer_class = ManagerGroupListSerializer

    def get_object(self):
        '''
        get `manager` group
        '''
        group = Group.valid_objects.filter(uid='manager').first()
        if not group:
            raise NotFound
        return group

    def get(self, request, *args, **kwargs):
        '''
        获取所有子管理员组
        '''
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ManagerGroupPageListAPIView(generics.ListAPIView):
    '''
    get manager group page in list
    '''

    permission_classes = [IsAuthenticated & IsAdminUser]
    serializer_class = GroupWithVerboseManagerGroup
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        group = Group.valid_objects.filter(uid='manager').first()
        if group:
            return Group.valid_objects.filter(parent=group)
        else:
            return []


class GroupChildUserAPIView(mixins.ListModelMixin, generics.RetrieveUpdateAPIView):
    '''
    组下属成员信息
    普通用户在可见范围内可读
    管理员可见可编辑
    '''

    serializer_class = UserSerializer
    pagination_class = DefaultListPaginator

    read_permission_classes = [
        IsAuthenticated & (NodeEmployeeReadable | IsManagerUser | IsAdminUser)
    ]
    write_permission_classes = [IsAuthenticated & (IsNodeManager | IsAdminUser)]

    def get_permissions(self):
        '''
        读写权限
        '''
        if self.request.method in SAFE_METHODS:
            return [perm() for perm in self.read_permission_classes]
        return [perm() for perm in self.write_permission_classes]

    def get_object(self):
        '''
        find group
        '''
        group = Group.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not group:
            raise NotFound
        self.check_object_permissions(self.request, group)
        return group

    def get_groups(self):
        '''
        find groups
        来自url中的uid和查询条件中的附加uid
        '''
        main_group = self.get_object()
        other_uids = self.request.query_params.get('uids', '').split('|')
        other_group = Group.valid_objects.filter(uid__in=other_uids)
        return set([main_group]) | set(other_group)

    def get(self, request, *args, **kwargs):
        '''
        支持在查询条件中加上其他group的uid，做为附加限制取交集
        这些附加group uid同样不会考虑间接附属关系
        '''
        user_ids = (
            GroupMember.valid_objects.filter(owner__in=self.get_groups())
            .values('user__id')
            .distinct()
        )
        queryset = User.valid_objects.filter(id__in=user_ids).order_by('id')

        filter_params_mapper = {
            'name': 'name__icontains',
            'username': 'username__icontains',
            'email': 'email__icontains',
            'mobile': 'mobile__icontains',
            'before_last_active_time': 'last_active_time__lte',
            'after_last_active_time': 'last_active_time__gte',
            'before_created': 'created__lte',
            'after_created': 'created__gte',
        }

        filters = {}
        for key, value in request.query_params.dict().items():
            if key in filter_params_mapper and value not in ['', None]:
                filters[filter_params_mapper[key]] = value

        queryset = queryset.filter(**filters).order_by('id')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @catch_json_load_error
    def update(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        '''
        调整成员
        '''
        group = self.get_object()
        data = json.loads(request.body.decode('utf-8'))

        subject = data.get('subject', '')
        if subject not in ['add', 'delete', 'sort', 'override', 'move_out']:
            raise ValidationError(
                {'subject': 'thid field must be one of add, delete, sort, override'}
            )

        inplace = False  # 目标组是否包括自身
        group_uids = set(get_patch_scope(request))
        if kwargs['uid'] in group_uids:
            inplace = True
            group_uids.remove(kwargs['uid'])

        groups = get_groups_from_uids(group_uids)
        users = get_users_from_uids(data.get('user_uids', []))

        if subject == 'move_out':
            for another_node in groups:
                update_users_of_owner(another_node, users, 'add')
            if not inplace:
                update_users_of_owner(group, users, 'delete')

        update_users_of_owner(group, users, subject)

        return Response(UserListSerializer(group).data)


class UsercenterGroupChildUserAPIView(GroupChildUserAPIView):
    read_permission_classes = [IsAuthenticated]
