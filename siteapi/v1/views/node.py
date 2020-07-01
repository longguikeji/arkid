'''
views for node
'''
# pylint: disable=line-too-long, cyclic-import
from functools import wraps

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.conf import settings
from django.urls import resolve
from oneid_meta.models import Dept, Group, AppGroup
from oneid_meta.models.mixin import TreeNode as Node
from siteapi.v1.serializers.appgroup import AppGroupTreeSerializer
from siteapi.v1.views import (
    dept as dept_view,
    group as group_view,
    perm as perm_view,
)
from siteapi.v1.serializers.dept import DeptTreeSerializer, DeptSerializer
from siteapi.v1.serializers.group import GroupTreeSerializer, GroupSerializer
from oneid.permissions import IsAdminUser, IsOrgMember, IsManagerUser, NodeEmployeeReadable


class MetaNodeAPIView(APIView):
    '''
    组织结构基本信息 [GET]
    '''

    def get_permissions(self):
        # pylint: disable=import-outside-toplevel,attribute-defined-outside-init
        from siteapi.v1.views.org import validity_check
        self.org = validity_check(self.kwargs['oid'])

        permission_classes = [IsAuthenticated & IsOrgMember(self.org)]

        return [perm() for perm in permission_classes]

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument, no-self-use
        '''
        获取组织结构基本信息
        '''
        data = {}
        if settings.SITE_META.lower() == 'native':
            custom_nodes = Group.valid_objects.filter(parent=self.org.group). \
                exclude(
                uid__in=[self.org.direct.uid, self.org.role.uid, self.org.label.uid, self.org.manager.uid]).order_by(
                'created')
            data = [
                {
                    'name':
                        '默认分类',
                    'slug':
                        'default',
                    'node_uid':
                        None,
                    'nodes': [{
                        'name': '部门',
                        'node_uid': self.org.dept.node_uid,
                        'node_subject': 'dept',
                    }, {
                        'name': '直属成员',
                        'node_uid': self.org.direct.node_uid,
                        'node_subject': 'direct',
                    }, {
                        'name': '角色',
                        'node_uid': self.org.role.node_uid,
                        'node_subject': 'role',
                    }, {
                        'name': '标签',
                        'node_uid': self.org.label.node_uid,
                        'node_subject': 'label',
                    },
                        #     {
                        #     'name': '管理员',
                        #     'node_uid': self.org.manager.node_uid,
                        #     'node_subject': 'manager',
                        # }
                    ]
                },
                {
                    'name':
                        '自定义分类',
                    'slug':
                        'custom',
                    'node_uid':
                        self.org.group.node_uid,
                    'nodes': [{
                        'name': node.name,
                        'node_uid': node.node_uid,
                        'node_subject': node.uid,
                    } for node in custom_nodes],
                },
            ]
        return Response(data)


def handle_exception(dispatch):
    '''
    处理异常
    '''

    @wraps(dispatch)
    def wrapper(self, request, *args, **kwargs):
        try:
            return dispatch(self, request, *args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            self.headers = self.default_response_headers
            response = self.handle_exception(exc)
            self.response = self.finalize_response(request, response, *args, **kwargs)
            return self.response

    return wrapper


NODE_MAPPING = {
    'depts': 'nodes',
    'groups': 'nodes',
}


def core_abstract_node(data):
    '''
    替换`dept`,`group`等关键字为`node`
    '''
    if isinstance(data, list):
        for index, item in enumerate(data):
            data[index] = core_abstract_node(item)
    elif isinstance(data, dict):
        for key, _value in list(data.items()):
            value = core_abstract_node(_value)
            if key in NODE_MAPPING:
                data[NODE_MAPPING[key]] = value
                data.pop(key)
            else:
                data[key] = value
    else:
        pass
    return data


def abstract_node(dispatch):
    '''
    将group、dept抽象成node
    '''

    @wraps(dispatch)
    def wrapper(self, request, *args, **kwargs):
        response = dispatch(self, request, *args, **kwargs)
        response.data = core_abstract_node(response.data)
        return response

    return wrapper


class NodeListAPIView(APIView):
    '''
    某节点下所有子孙节点列表，包括该节点自身
    '''

    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']

        if uid.startswith(Dept.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Dept.NODE_PREFIX, '', 1)
            return dept_view.DeptScopeListAPIView().dispatch(request, *args, **kwargs)
        if uid.startswith(Group.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Group.NODE_PREFIX, '', 1)
            return group_view.GroupScopeListAPIView().dispatch(request, *args, **kwargs)
        raise ValidationError({'uid': 'this field must start with `d_` or `g_`'})


class NodeDetailAPIView(APIView):
    '''
    以管理员身份管理节点
    '''

    @abstract_node
    @handle_exception
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']

        if uid.startswith(Dept.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Dept.NODE_PREFIX, '', 1)
            return dept_view.DeptDetailAPIView().dispatch(request, *args, **kwargs)
        if uid.startswith(Group.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Group.NODE_PREFIX, '', 1)
            return group_view.GroupDetailAPIView().dispatch(request, *args, **kwargs)
        raise ValidationError({'uid': 'this field must start with `d_` or `g_`'})


class UcenterNodeDetailAPIView(generics.RetrieveAPIView):
    '''
    以普通用户身份获取节点信息
    '''

    permission_classes = [IsAuthenticated & NodeEmployeeReadable]

    def get_object(self):
        '''
        find node
        '''
        node, node_subject = Node.retrieve_node(self.kwargs['uid'])
        if node is None:
            raise NotFound

        try:
            self.check_object_permissions(self.request, node)
        except PermissionDenied:
            raise NotFound

        if node_subject == 'dept':
            self.serializer_class = DeptSerializer
        else:
            self.serializer_class = GroupSerializer
        return node


class NodeTreeAPIView(generics.RetrieveAPIView):
    '''
    获取节点结构树，以该节点为root
    '''

    permission_classes = [IsAuthenticated]

    user_required = False
    user_identity = 'employee'

    def get_object(self):
        """
        find node
        """
        node, _ = Node.retrieve_node(self.kwargs['uid'])
        if node is None:
            raise NotFound

        if node.__class__ == Dept:
            self.serializer_class = DeptTreeSerializer
        elif node.__class__ == Group:
            self.serializer_class = GroupTreeSerializer
        elif node.__class__ == AppGroup:
            self.serializer_class = AppGroupTreeSerializer
        return node

    def get_serializer_context(self):
        """
        - user_required: 是否返回用户数据
        - app_required: 是否返回应用数据 TODO
        """
        context = super().get_serializer_context()
        self.user_required = self.request.query_params.get('user_required', False) not in (False, 'false', 'False')
        context['user_required'] = self.user_required
        url_name = resolve(self.request.path_info).url_name
        context['url_name'] = url_name
        context['user_identity'] = self.user_identity
        return context

    def retrieve(self, request, *args, **kwargs):
        '''
        获取节点结构树
        '''

        node = self.get_object()
        serializer = self.get_serializer(node)
        data = serializer.trim_visible_tree()
        if data is None:
            raise NotFound
        if self.user_required:
            serializer.aggregate_headcount(data)
        return Response(data)


class ManagerNodeTreeAPIView(NodeTreeAPIView):
    '''
    以管理员身份获取节点结构树，以该节点为root
    '''

    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    user_identity = 'manager'


class UcenterNodeTreeAPIView(NodeTreeAPIView):
    '''
    以普通用户身份获取节点结构树，以该节点为root
    '''

    permission_classes = [IsAuthenticated]

    user_identity = 'employee'


class NodeChildNodeAPIView(APIView):
    '''
    某节点的子节点
    '''

    @abstract_node
    @handle_exception
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']

        if uid.startswith(Dept.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Dept.NODE_PREFIX, '', 1)
            return dept_view.DeptChildDeptAPIView().dispatch(request, *args, **kwargs)
        if uid.startswith(Group.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Group.NODE_PREFIX, '', 1)
            return group_view.GroupChildGroupAPIView().dispatch(request, *args, **kwargs)
        raise ValidationError({'uid': 'this field must start with `d_` or `g_`'})


class NodeChildUserAPIView(APIView):
    '''
    节点下属成员
    '''

    @abstract_node
    @handle_exception
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']

        if uid.startswith(Dept.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Dept.NODE_PREFIX, '', 1)
            return dept_view.DeptChildUserAPIView().dispatch(request, *args, **kwargs)
        if uid.startswith(Group.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Group.NODE_PREFIX, '', 1)
            return group_view.GroupChildUserAPIView().dispatch(request, *args, **kwargs)
        raise ValidationError({'uid': 'this field must start with `d_` or `g_`'})


class NodePermAPIView(APIView):
    '''
    节点权限
    '''

    @abstract_node
    @handle_exception
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']

        if uid.startswith(Dept.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Dept.NODE_PREFIX, '', 1)
            return perm_view.DeptPermView().dispatch(request, *args, **kwargs)
        if uid.startswith(Group.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Group.NODE_PREFIX, '', 1)
            return perm_view.GroupPermView().dispatch(request, *args, **kwargs)
        raise ValidationError({'uid': 'this field must start with `d_` or `g_`'})
