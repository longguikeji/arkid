'''
views about dept
- DeptTree
- DeptChildDept
- DeptMemberUser
'''
# pylint: disable=attribute-defined-outside-init, cyclic-import
import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.exceptions import (
    NotFound,
    ValidationError,
    PermissionDenied,
)

from oneid_meta.models import Dept
from oneid.permissions import (
    IsNodeManager,
    IsAdminUser,
    IsManagerUser,
    IsOrgOwnerOf,
    NodeManagerReadable,
)
from siteapi.v1.serializers.user import UserListSerializer, UserSerializer
from siteapi.v1.serializers.dept import (
    DeptTreeSerializer,
    DeptListSerializer,
    DeptSerializer,
    DeptDetailSerializer,
)
from siteapi.v1.views.utils import (
    get_users_from_uids,
    get_depts_from_uids,
    update_users_of_owner,
    gen_uid,
)
from siteapi.v1.views import node as node_views
from executer.core import CLI
from common.django.drf.paginator import DefaultListPaginator
from common.django.drf.views import catch_json_load_error


class DeptListAPIView(generics.ListAPIView):
    '''
    get depts in list

    管理员可见
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]
    serializer_class = DeptSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        '''
        filter depts
        '''
        kwargs = {}
        name = self.request.query_params.get('name', None)
        if name:
            kwargs.update(name__icontains=name)

        return Dept.valid_objects.filter(**kwargs).exclude(uid='root').order_by('id')


class DeptScopeListAPIView(generics.ListAPIView):
    '''
    指定节点下属的所有节点，包括该节点自身 [GET]

    管理员可见
    '''
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    serializer_class = DeptTreeSerializer

    def get_object(self):
        '''
        find dept
        '''
        dept = Dept.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not dept:
            raise NotFound
        return dept

    def get(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        以列表形式输出指定节点下属的所有节点
        '''
        node = self.get_object()
        serializer = self.get_serializer(node, context={'url_name': 'dept_scope_list'})
        data = serializer.data
        if data is None:
            raise NotFound
        nodes = list(serializer.flat_tree(data))
        if nodes:
            nodes[0]['parent_uid'] = node.parent_uid
            nodes[0]['parent_node_uid'] = node.parent_node_uid
        return Response(nodes)


class DeptDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    部门信息 [GET] [PATCH] [DELETE]

    普通用户有可能可读
    '''
    serializer_class = DeptDetailSerializer

    def get_permissions(self):
        '''
        读写权限
        '''
        self.dept = Dept.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not self.dept:
            raise NotFound

        org = self.dept.org
        if not org:
            return []

        read_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(org) | NodeManagerReadable)]
        write_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(org) | IsNodeManager)]

        if self.request.method in SAFE_METHODS:
            return [perm() for perm in read_permission_classes]
        return [perm() for perm in write_permission_classes]

    def get_object(self):
        '''
        find dept
        '''
        try:
            self.check_object_permissions(self.request, self.dept)
        except PermissionDenied as exc:
            if self.request.method in SAFE_METHODS:
                raise NotFound
            raise exc
        self.dept.refresh_visibility_scope()
        return self.dept

    def perform_destroy(self, instance):
        '''
        删除组
        '''
        if self.request.query_params.get('ignore_user', '') in ('true', 'True'):
            CLI().delete_users_from_dept(instance.users, instance)
        CLI().delete_dept(instance)

    @catch_json_load_error
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        更新部门信息
        '''
        dept = self.get_object()
        data = json.loads(request.body.decode('utf-8'))
        dept = CLI().update_dept(dept, data)
        return Response(self.get_serializer(dept).data)


class ManagerDeptTreeAPIView(APIView):
    '''
    管理员身份部门结构树 [GET]
    '''
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']
        node_uid = Dept.NODE_PREFIX + uid
        kwargs['uid'] = node_uid
        return node_views.ManagerNodeTreeAPIView().dispatch(request, *args, **kwargs)


class UcenterDeptTreeAPIView(APIView):
    '''
    普通用户身份部门结构树 [GET]
    '''
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']
        node_uid = Dept.NODE_PREFIX + uid
        kwargs['uid'] = node_uid
        return node_views.UcenterNodeTreeAPIView().dispatch(request, *args, **kwargs)


def get_patch_scope(request):
    '''
    操作范围
    '''
    data = request.data
    dept_uids = []
    node_uids = data.get('node_uids', [])
    if node_uids:
        for node_uid in node_uids:
            if node_uid.startswith(Dept.NODE_PREFIX):
                dept_uids.append(node_uid.replace(Dept.NODE_PREFIX, '', 1))
    else:
        dept_uids = data.get('dept_uids', [])
    return dept_uids


class DeptChildDeptAPIView(
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        generics.ListCreateAPIView,
):
    '''
    部门下属子部门信息

    管理员可见
    TODO: 权限校验需深入
    '''
    serializer_class = DeptListSerializer

    def get_object(self):
        '''
        find dept
        '''
        self.check_object_permissions(self.request, self.dept)
        return self.dept

    def get_permissions(self):
        '''
        读写权限
        '''
        self.dept = Dept.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not self.dept:
            raise NotFound

        self.org = self.dept.org
        if not self.org:
            return []

        read_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | NodeManagerReadable)]
        write_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | IsNodeManager)]

        if self.request.method in SAFE_METHODS:
            return [perm() for perm in read_permission_classes]
        return [perm() for perm in write_permission_classes]

    def get(self, request, *args, **kwargs):
        '''
        获取部门下属子部门信息 [GET]
        '''
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @catch_json_load_error
    def create(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        添加子部门,从无到有 [POST]
        '''
        parent_dept = self.get_object()
        dept_data = json.loads(request.body.decode('utf-8'))
        uid = dept_data.get('uid', '')
        if not uid:
            name = dept_data.get('name')
            uid = gen_uid(name=name, cls=Dept)
            dept_data['uid'] = uid
        dept_data.update(parent_uid=self.kwargs['uid'])
        cli = CLI()
        child_dept = cli.create_dept(dept_data, self.org)
        cli.add_dept_to_dept(child_dept, parent_dept)
        return Response(DeptDetailSerializer(child_dept).data, status=status.HTTP_201_CREATED)

    @catch_json_load_error
    def patch(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        调整子部门 [PATCH]
        目前应只需要排序和移入
        '''
        parent_dept = self.get_object()
        data = json.loads(request.body.decode('utf-8'))
        subject = data.get('subject', '')
        if subject not in ['sort', 'add']:
            raise ValidationError({'subject': ['this field must be `sort` or `add`']})

        filters = {}
        if subject == 'sort':
            filters = {'parent': parent_dept}

        dept_uids = get_patch_scope(request)
        try:
            depts = Dept.get_from_pks(pks=dept_uids, pk_name='uid', raise_exception=True, **filters)
        except ObjectDoesNotExist as error:
            bad_uid = error.args[0]
            raise ValidationError({'dept_uids': ['dept:{} invalid'.format(bad_uid)]})

        cli = CLI()
        if subject == 'sort':
            cli.sort_depts_in_dept(depts, parent_dept)
        elif subject == 'add':
            for dept in depts:
                if dept.parent != parent_dept:
                    cli.move_dept_to_dept(dept, parent_dept)

        return Response(DeptListSerializer(parent_dept).data)


class DeptChildUserAPIView(mixins.ListModelMixin, generics.RetrieveUpdateAPIView):
    '''
    部门下属成员信息

    仅拥有此管理范围的管理员可见可编辑
    '''
    # serializer_class = EmployeeSerializer
    serializer_class = UserSerializer
    pagination_class = DefaultListPaginator

    def get_permissions(self):
        '''
        读写权限
        '''
        self.dept = Dept.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not self.dept:
            raise NotFound

        org = self.dept.org
        if not org:
            return []

        read_permission_classes = [IsAuthenticated & (IsNodeManager | IsAdminUser | IsOrgOwnerOf(org))]
        write_permission_classes = [IsAuthenticated & (IsNodeManager | IsAdminUser | IsOrgOwnerOf(org))]

        if self.request.method in SAFE_METHODS:
            return [perm() for perm in read_permission_classes]
        return [perm() for perm in write_permission_classes]

    def get_object(self):
        '''
        find dept
        '''
        self.check_object_permissions(self.request, self.dept)
        return self.dept

    def get(self, request, *args, **kwargs):
        queryset = self.get_object().users
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        '''
        add org to serializer context
        '''
        context = super().get_serializer_context()
        context['org'] = self.get_object().org
        return context

    @catch_json_load_error
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        调整成员
        - add
            将一批人加入该部门

        - delete
            将一批人从该部门删除

        - move_out
            将一批人从该部门移除，并加入到指定其他部门
            等效于 self.delete + others.add
            当不指定其他部门时，即`delete`
        '''
        dept = self.get_object()
        data = json.loads(request.body.decode('utf-8'))

        subject = data.get('subject', '')
        if subject not in ['add', 'delete', 'sort', 'override', 'move_out']:
            raise ValidationError({'subject': 'thid field must be one of add, delete, sort, override, move_out'})

        inplace = False    # 目标部门是否包括自身
        dept_uids = set(get_patch_scope(request))
        if kwargs['uid'] in dept_uids:
            inplace = True
            dept_uids.remove(kwargs['uid'])

        depts = get_depts_from_uids(dept_uids)
        users = get_users_from_uids(data.get('user_uids', []))

        if subject == 'move_out':
            for another_dept in depts:
                update_users_of_owner(another_dept, users, 'add')
            if not inplace:
                update_users_of_owner(dept, users, 'delete')
        else:
            update_users_of_owner(dept, users, subject)

        return Response(UserListSerializer(dept).data)
