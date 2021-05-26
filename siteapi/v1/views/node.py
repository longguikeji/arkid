'''
views for node
'''

from functools import wraps

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.conf import settings
from django.urls import resolve
from oneid_meta.models import Dept, Group
from oneid_meta.models.mixin import TreeNode as Node
from siteapi.v1.views import (
    dept as dept_view,
    group as group_view,
    perm as perm_view,
)
from siteapi.v1.serializers.dept import DeptCash, DeptSerializer, DeptTreeSerializer
from siteapi.v1.serializers.group import GroupTreeSerializer, GroupSerializer
from oneid.permissions import IsAdminUser, IsManagerUser, NodeEmployeeReadable
from oneid_meta.models.group import GroupMember, ManagerGroup
from oneid_meta.models.dept import DeptMember
from oneid.statistics import TimeCash
from siteapi.v1.serializers import UserLiteSerializer


class MetaNodeAPIView(APIView):
    '''
    组织结构基本信息 [GET]
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):    # pylint: disable=unused-argument, no-self-use
        '''
        获取组织结构基本信息
        '''
        data = {}
        if settings.SITE_META.lower() == 'native':
            custom_nodes = Group.valid_objects.filter(parent__uid='intra').\
                exclude(uid__in=['role', 'label', 'manager']).order_by('created')
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
                        'node_uid': 'd_root',
                        'node_subject': 'dept',
                    }, {
                        'name': '角色',
                        'node_uid': 'g_role',
                        'node_subject': 'role',
                    }, {
                        'name': '标签',
                        'node_uid': 'g_label',
                        'node_subject': 'label',
                    }]
                },
                {
                    'name':
                    '自定义分类',
                    'slug':
                    'custom',
                    'node_uid':
                    'g_intra',
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
        except Exception as exc:    # pylint: disable=broad-except
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
        '''
        find node
        '''
        node, _ = Node.retrieve_node(self.kwargs['uid'])
        if node is None:
            raise NotFound

        if node.__class__ == Dept:
            self.serializer_class = DeptTreeSerializer
        else:
            self.serializer_class = GroupTreeSerializer
        return node

    def get_serializer_context(self):
        '''
        - user_required: 是否返回用户数据
        '''
        context = super().get_serializer_context()
        self.user_required = self.request.query_params.get('user_required', False) not in (False, 'false', 'False')
        context['user_required'] = self.user_required
        url_name = resolve(self.request.path_info).url_name
        context['url_name'] = url_name
        context['user_identity'] = self.user_identity
        return context

    def legacy_retrieve(self, request, *args, **kwargs):
        '''
        获取节点结构树
        '''
        
        DeptCash.clear()
        node = self.get_object()
        serializer = self.get_serializer(node)
        data = serializer.trim_visible_tree()
        if data is None:
            raise NotFound
        if self.user_required:
            serializer.aggregate_headcount(data)
        TimeCash.over()
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        if self.user_identity == 'employee':
            return self.legacy_retrieve(request, *args, **kwargs)
        node = self.get_object()
        if node.__class__ == Dept:
            return self.retrieve_dept(node, request, *args, **kwargs)
        else:
            return self.legacy_retrieve(request, *args, **kwargs)

    def retrieve_dept(self, node, request, *args, **kwargs):
        if self.request.user.is_admin:
            sub_depts = Dept.valid_objects.filter(parent=node)
            data = self.get_response_data(node, sub_depts)
            return Response(data)
        if node.uid == 'root':
            # 子管理员根据管理组的类型返回不同的节点
            sub_depts = self.get_sub_manager_depts(request.user)
            data = self.get_response_data(node, sub_depts)
            return Response(data)
        else:
            # 判断node是否在当前用户管理范围内
            # 如果是在当前用户类型1（所在节点及下属节点）的管理下，返回当前及子几点
            # 如果是在当前用户类型2（指定节点）只返回当前节点，不返回子节点，
            # 否则放回{}

            upstream_uids = set(node.upstream_uids)
            for manager_group in request.user.manager_groups:
                if manager_group.scope_subject == 1:  # 所在节点及下属节点
                    if upstream_uids & set(request.user.node_uids):
                        sub_depts = Dept.valid_objects.filter(parent=node)
                        data = self.get_response_data(node, sub_depts)
                        return Response(data)
                if manager_group.scope_subject == 2:  # 指定节点、人
                    if node.node_uid in manager_group.nodes:
                        data = self.get_response_data(node, [])
                        return Response(data)
            return Response({})

    def get_sub_manager_depts(self, user):
        depts = {}
        for mg in self.request.user.manager_groups:
            scope_1_count = 0
            dd = []
            if mg.scope_subject == 1:
                if scope_1_count > 0:
                    continue
                dd = Dept.valid_objects.filter(
                    id__in=DeptMember.valid_objects.values('owner')
                    .filter(user=user)
                    .distinct()
                )
            else:
                uids = []
                for node in mg.nodes:
                    uids.append(node.replace('d_', ''))
                dd = Dept.valid_objects.filter(uid__in=uids)

            for d in dd:
                if d.uid not in depts:
                    depts[d.uid] = d
                else:
                    continue
        return depts.values()

    def get_response_data(self, father_dept, sub_depts):
        nodes = []
        if sub_depts:
            for sub in sub_depts:
                nodes.append(self.get_response_data(sub, []))
        users = self.get_users(father_dept)
        return {
            'info': self.get_info(father_dept),
            'users': users,
            'nodes': nodes,
            'headcount': len(users),  # 只返回当前节点下面用户数量
        }

    def get_info(self, instance):
        '''
        只返回基本信息
        '''
        return {
            'dept_id': instance.id,
            'node_uid': instance.node_uid,
            'node_subject': instance.node_subject,
            'uid': instance.uid,
            'name': instance.name,
            'remark': instance.remark,
        }

    def get_users(self, instance):
        return UserLiteSerializer(instance.users, many=True).data



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

class UcenterNodeChildUserAPIView(APIView):
    '''
    todo: 以普通用户身份获取节点user
    '''
    @abstract_node
    @handle_exception
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']

        if uid.startswith(Dept.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Dept.NODE_PREFIX, '', 1)
            return dept_view.UsercenterDeptChildUserAPIView().dispatch(request, *args, **kwargs)
        if uid.startswith(Group.NODE_PREFIX):
            kwargs['uid'] = uid.replace(Group.NODE_PREFIX, '', 1)
            return group_view.UsercenterGroupChildUserAPIView().dispatch(request, *args, **kwargs)
        raise ValidationError({'uid': 'this field must start with `d_` or `g_`'})

class UcenterNodeChildNodeAPIView(APIView):
    '''
    todo: 以普通用户身份获取节点子节点
    '''
    # @abstract_node
    # @handle_exception
    # def dispatch(self, request, *args, **kwargs):
    #     uid = kwargs['uid']

    #     if uid.startswith(Dept.NODE_PREFIX):
    #         kwargs['uid'] = uid.replace(Dept.NODE_PREFIX, '', 1)
    #         return dept_view.UsercenterDeptChildUserAPIView().dispatch(request, *args, **kwargs)
    #     if uid.startswith(Group.NODE_PREFIX):
    #         kwargs['uid'] = uid.replace(Group.NODE_PREFIX, '', 1)
    #         return group_view.UsercenterGroupChildGroupAPIView().dispatch(request, *args, **kwargs)
    #     raise ValidationError({'uid': 'this field must start with `d_` or `g_`'})

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
