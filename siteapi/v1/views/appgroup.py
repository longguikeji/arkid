"""
view about app group
- AppGroupChildAppGroup
"""
import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, mixins, status
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from common.django.drf.paginator import DefaultListPaginator
from common.django.drf.views import catch_json_load_error
from executer.core import CLI
from oneid.permissions import IsAdminUser, IsOrgOwnerOf, NodeManagerReadable, IsNodeManager, CustomPerm, IsManagerOf
from oneid_meta.models import AppGroup, APP
from oneid_meta.models.appgroup import AppGroupMember
from siteapi.v1.serializers.app import APPWithAccessOwnerSerializer, APPListSerializer
from siteapi.v1.serializers.appgroup import AppGroupListSerializer, AppGroupDetailSerializer
from siteapi.v1.views.utils import gen_uid, get_app_groups_from_uids, get_apps_from_ids, update_apps_of_owner
from siteapi.v1.views import node as node_views


class AppGroupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    应用分组的信息 [GET] [PATCH] [DELETE]
    """
    serializer_class = AppGroupDetailSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_group = None

    def get_permissions(self):
        """
        读写权限
        """
        self.app_group = AppGroup.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not self.app_group:
            raise NotFound

        org = self.app_group.org
        if not org:
            return []

        read_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(org) | NodeManagerReadable)]
        write_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(org) | IsNodeManager)]

        if self.request.method in SAFE_METHODS:
            return [perm() for perm in read_permission_classes]
        return [perm() for perm in write_permission_classes]

    def get_object(self):
        """
        find app group
        """
        try:
            self.check_object_permissions(self.request, self.app_group)
        except PermissionDenied as exc:
            if self.request.method in SAFE_METHODS:
                raise NotFound
            raise exc
        self.app_group.refresh_visibility_scope()
        return self.app_group

    def perform_destroy(self, instance):
        """
        delete app group
        """
        # TODO 考虑是否删除应用
        # if self.request.query_params.get('ignore_app', '') in ('true', 'True'):
        #     CLI().delete_apps_from_group(instance.users, instance)
        CLI().delete_app_group(instance)

    @catch_json_load_error
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        update app group
        """
        app_group = self.get_object()
        data = json.loads(request.body.decode('utf-8'))
        app_group = CLI().update_app_group(app_group, data)
        return Response(self.get_serializer(app_group).data)


class AppGroupChildAppGroupAPIView(
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        generics.ListCreateAPIView,
):
    """
    应用分组下属子应用分组信息 [GET], [POST], [PATCH]
    管理员可见
    """
    serializer_class = AppGroupListSerializer

    def __init__(self, **kwargs):
        super(AppGroupChildAppGroupAPIView, self).__init__(**kwargs)
        self.app_group = None
        self.org = None

    def get_permissions(self):
        """
        读写权限
        """
        # pylint: disable=invalid-name
        self.app_group = AppGroup.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not self.app_group:
            raise NotFound

        self.org = self.app_group.org
        if not self.org:
            return []

        read_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | NodeManagerReadable)]
        write_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | IsNodeManager)]
        create_category_permission_classes = [
            IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | CustomPerm(f'{self.org.oid}_category_create'))
        ]

        if self.request.method in SAFE_METHODS:
            permissions = read_permission_classes
        elif self.app_group.is_org and self.request.method == 'POST':
            permissions = create_category_permission_classes
        else:
            permissions = write_permission_classes

        return [perm() for perm in permissions]

    def get_object(self):
        """
        find app group
        """
        self.check_object_permissions(self.request, self.app_group)
        return self.app_group

    def get(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        获取应用分组下属子应用分组信息 [GET]
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        添加子应用分组,从无到有 [POST]
        """
        parent_app_group = self.get_object()
        app_group_data = request.data
        # if 'manager_group' in group_data:
        #     if parent_group.is_org_manager:
        #         if not group_data.get('name', ''):
        #             name = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
        #             group_data.update(name=name)
        #     else:
        #         group_data.pop('manager_group')
        if not app_group_data.get('uid', ''):
            name = app_group_data.get('name')
            if not name:
                raise ValidationError({'name': ['this field is required']})
            uid = gen_uid(name=name, cls=AppGroup)
            app_group_data['uid'] = uid

        cli = CLI()
        app_group_data.update(parent_uid=self.kwargs['uid'])
        child_app_group = cli.create_app_group(app_group_data, self.org)
        cli.add_appgroup_to_appgroup(child_app_group, parent_app_group)
        # if parent_group.is_org:
        #     self._auto_create_manager_group(request, child_group)
        return Response(AppGroupDetailSerializer(child_app_group).data, status=status.HTTP_201_CREATED)

    @catch_json_load_error
    def patch(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        调整应用分组子组 [PATCH]
        操作包括
        - 排序sort
        - 移动add, 即修改父部门。从无到有的添加，由create负责
        """
        parent_app_group = self.get_object()
        data = json.loads(request.body.decode('utf-8'))
        subject = data.get('subject', '')
        if subject not in ['sort', 'add']:
            raise ValidationError({'subject': ['this field must be `sort` or `add`']})

        filters = {}
        if subject == 'sort':
            filters = {'parent': parent_app_group}

        app_group_uids = get_patch_scope(request)

        try:
            app_groups = AppGroup.get_from_pks(pks=app_group_uids, pk_name='uid', raise_exception=True, **filters)
        except ObjectDoesNotExist as error:
            bad_uid = error.args[0]
            raise ValidationError({'app_group_uids': ['app_group:{} invalid'.format(bad_uid)]})

        cli = CLI()
        if subject == 'sort':
            cli.sort_appgroups_in_appgroup(app_groups, parent_app_group)
        elif subject == 'add':
            for app_group in app_groups:
                cli.move_appgroup_to_appgroup(app_group, parent_app_group)
        return Response(AppGroupListSerializer(parent_app_group).data)


class AppGroupChildAppAPIView(mixins.ListModelMixin, generics.RetrieveUpdateAPIView):
    """
    应用分组下属成员应用的信息

    普通用户在可见范围内可读
    管理员可见可编辑
    """
    serializer_class = APPWithAccessOwnerSerializer
    pagination_class = DefaultListPaginator

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_group = None

    def get_permissions(self):
        """
        读写权限
        """
        self.app_group = AppGroup.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not self.app_group:
            raise NotFound

        org = self.app_group.org
        if not org:
            return []

        read_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(org) | IsManagerOf(org))]
        write_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(org) | IsNodeManager)]

        if self.request.method in SAFE_METHODS:
            return [perm() for perm in read_permission_classes]
        return [perm() for perm in write_permission_classes]

    def get_object(self):
        """
        find app group
        """
        self.check_object_permissions(self.request, self.app_group)
        return self.app_group

    def get_groups(self):
        """
        find app groups
        来自url中的uid和查询条件中的附加uid
        """
        main_app_group = self.get_object()
        other_uids = self.request.query_params.get('uids', '').split('|')
        other_group = AppGroup.valid_objects.filter(uid__in=other_uids)
        return set([main_app_group]) | set(other_group)

    def get(self, request, *args, **kwargs):
        """
        支持在查询条件中加上其他app group的uid，做为附加限制取交集
        这些附加app group uid同样不会考虑间接附属关系
        """
        app_ids = AppGroupMember.valid_objects. \
            filter(owner__in=self.get_groups()). \
            values('app__id'). \
            distinct()
        queryset = APP.valid_objects.filter(id__in=app_ids).order_by('id')

        filter_params_mapper = {
            'name': 'name__icontains',
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
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        """
        add org to serializer context
        """
        context = super().get_serializer_context()
        context['org'] = self.get_object().org
        return context

    @catch_json_load_error
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        调整应用成员
        """
        app_group = self.get_object()
        data = json.loads(request.body.decode('utf-8'))

        subject = data.get('subject', '')
        if subject not in ['add', 'delete', 'sort', 'override', 'move_out']:
            raise ValidationError({'subject': 'this field must be one of add, delete, sort, override'})

        inplace = False    # 目标组是否包括自身
        app_group_uids = set(get_patch_scope(request))
        if kwargs['uid'] in app_group_uids:
            inplace = True
            app_group_uids.remove(kwargs['uid'])

        app_groups = get_app_groups_from_uids(app_group_uids)
        apps = get_apps_from_ids(data.get('app_ids', []))

        if subject == 'move_out':
            for another_node in app_groups:
                update_apps_of_owner(another_node, apps, 'add')
            if not inplace:
                update_apps_of_owner(app_group, apps, 'delete')
            return Response(APPListSerializer(app_group).data)

        update_apps_of_owner(app_group, apps, subject)
        return Response(APPListSerializer(app_group).data)


class ManagerAppGroupTreeAPIView(APIView):
    """
    管理员身份组结构树 [GET]
    """
    def dispatch(self, request, *args, **kwargs):
        uid = kwargs['uid']
        node_uid = AppGroup.NODE_PREFIX + uid
        kwargs['uid'] = node_uid
        return node_views.ManagerNodeTreeAPIView().dispatch(request, *args, **kwargs)


def get_patch_scope(request):
    """
    操作范围
    """
    data = request.data
    # app_group_uids = []
    node_uids = data.get('node_uids', [])
    if node_uids:
        # for node_uid in node_uids:
        #     if node_uid.startswith(AppGroup.NODE_PREFIX):
        #         app_group_uids.append(node_uid.replace(AppGroup.NODE_PREFIX, '', 1))
        app_group_uids = [
            node_uid.replace(AppGroup.NODE_PREFIX, '', 1) for node_uid in node_uids
            if node_uid.startswith(AppGroup.NODE_PREFIX)
        ]
    else:
        app_group_uids = data.get('app_group_uids', [])
    return app_group_uids
