# pylint: disable=too-many-lines
"""
views about perm
- PermList
- PermDetail
"""
import json

from rest_framework import generics, status, mixins
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, NotFound, MethodNotAllowed, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from oneid_meta.models import (Perm, UserPerm, DeptPerm, GroupPerm, User, Dept, Group, APP)
from siteapi.v1.serializers.perm import (
    PermSerializer,
    PermWithOwnerSerializer,
    OwnerSerializer,
    PermResultSerializer,
    UserPermResultSerializer,
    UserPermDetailSerializer,
)
from common.django.drf.paginator import DefaultListPaginator
from common.django.drf.views import catch_json_load_error
from oneid.permissions import IsAdminUser, IsManagerUser
from executer.log.rdb import LOG_CLI
from tasksapp.tasks import update_user_perm_in_db


class PermListCreateAPIView(generics.ListCreateAPIView):
    """
    权限列表 [GET],[POST]
    """
    pagination_class = DefaultListPaginator
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PermWithOwnerSerializer
        return PermSerializer

    def get_queryset(self):
        """
        :return: queryset for list [GET]
        """
        kwargs = {}
        subject = self.request.query_params.get('subject', '')
        if subject:
            kwargs.update(subject=subject)

        name = self.request.query_params.get('name', '')
        if name:
            kwargs.update(name__icontains=name)

        action_except = self.request.query_params.get('action_except', '')
        if action_except:
            kwargs.update(action_except=action_except)

        action = self.request.query_params.get('action', '')
        if action:
            kwargs.update(action__startswith=action)
            kwargs.pop('action_except', '')

        scope = self.request.query_params.get('scope', '')
        if scope:
            kwargs.update(scope=scope)

        if 'action_except' in kwargs:
            action_except = kwargs.pop('action_except')
            queryset = Perm.valid_objects.filter(**kwargs).exclude(action__startswith=action_except).order_by('id')
        else:
            queryset = Perm.valid_objects.filter(**kwargs).order_by('id')

        return queryset

    @transaction.atomic()
    def create(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        create perm [POST]
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 超管可以任意创建权限，子管理员只能为自己管理范围内的应用创建权限
        app_uid = serializer.validated_data.get('scope')
        user = request.user
        if not user.is_admin:
            app = APP.valid_objects.filter(uid=app_uid).first()
            if not (app and app.under_manage(user)):
                raise PermissionDenied

        self.perform_create(serializer)
        perm = serializer.instance

        # TODO: async
        for user in User.valid_objects.get_queryset():
            UserPerm.valid_objects.create(owner=user, perm=perm)

        for group in Group.valid_objects.get_queryset():
            GroupPerm.valid_objects.create(owner=group, perm=perm)

        for dep in Dept.valid_objects.get_queryset():
            DeptPerm.valid_objects.create(owner=dep, perm=perm)

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(serializer.data))

    def perform_create(self, serializer):
        super().perform_create(serializer)    # pylint: disable=no-member
        cli = LOG_CLI()
        cli.create_perm(serializer.instance)


class PermDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    特定权限信息 [GET], [PATCH], [DELETE]
    """
    serializer_class = PermSerializer
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_object(self):
        """
        find perm
        """
        perm = Perm.valid_objects.get_queryset().filter(uid=self.kwargs['uid']).first()
        if not perm:
            raise NotFound
        if not perm.under_manage(self.request.user):
            raise PermissionDenied
        return perm

    def retrieve(self, request, *args, **kwargs):
        """
        return perm detail [GET]
        """
        perm = self.get_object()
        return Response(self.get_serializer(perm).data)

    @catch_json_load_error
    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        update perm detail [PATCH]
        """
        perm = self.get_object()
        data = json.loads(request.body.decode('utf-8'))

        serializer = self.get_serializer(perm, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        '''
        硬删除
        '''
        if not instance.editable:
            raise MethodNotAllowed('DELETE protected perm')
        instance.kill()
        cli = LOG_CLI()
        cli.delete_perm(instance)


class PermOwnerAPIView(generics.ListAPIView, generics.UpdateAPIView):
    '''
    获取权限所有者[GET]
    '''

    serializer_class = OwnerSerializer
    pagination_class = DefaultListPaginator
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_object(self):
        '''
        return perm
        '''
        perm = Perm.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not perm:
            raise NotFound
        if not perm.under_manage(self.request.user):
            raise PermissionDenied
        return perm

    def get_queryset(self):
        perm = self.get_object()
        kwargs = {'perm': perm}

        _status = self.request.query_params.get('status', None)
        if _status is not None:
            if not _status in ('-1', '0', '1'):
                raise ValidationError({'status': ['this field must be one of -1, 0, 1']})
            kwargs.update({'status': _status})

        value = self.request.query_params.get('value', None)
        if value is not None:
            if value in ('true', 'True', True):
                kwargs.update(value=True)
            elif value in ('false', 'False', False):
                kwargs.update(value=False)

        owner_subject = self.request.query_params.get('owner_subject', 'all')

        if owner_subject == 'all':    #  TODO: 优化
            return list(UserPerm.valid_objects.filter(**kwargs)) + \
                list(DeptPerm.valid_objects.filter(**kwargs)) + \
                list(GroupPerm.valid_objects.filter(**kwargs))

        if owner_subject == 'user':
            owners = UserPerm.valid_objects.filter(**kwargs)
        elif owner_subject == 'dept':
            owners = DeptPerm.valid_objects.filter(**kwargs)
        else:
            owners = GroupPerm.valid_objects.filter(owner__top=owner_subject, **kwargs)

        return owners

    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument, too-many-locals
        '''
        黑白名单局部操作
        '''
        perm = self.get_object()
        clean = self.request.data.get('clean', False)
        if clean:
            UserPerm.valid_objects.filter(perm=perm).update(status='0')
            DeptPerm.valid_objects.filter(perm=perm).update(status='0')
            GroupPerm.valid_objects.filter(perm=perm).update(status='0')

        user_perm_status = self.request.data.get('user_perm_status', [])
        for ups in user_perm_status:
            user = User.valid_objects.filter(username=ups['uid']).first()
            # TODO: 目前对每个对象都逐一检验 under_manage，开销大; 且对于没有权限的，只是静默跳过，没有提示。需改进。
            if not (user and user.under_manage(request.user)):
                raise ValidationError({'user_perm_status': [f'invlid uid: `{ups["uid"]}`']})
            ups['instance'] = user

        node_perm_status = self.request.data.get('node_perm_status', [])
        for nps in node_perm_status:
            node, _ = Dept.retrieve_node(nps['uid'])
            if not (node and node.under_manage(request.user)):
                raise ValidationError({'node_perm_status': [f'invlid uid: `{nps["uid"]}`']})
            nps['instance'] = node

        for ups in user_perm_status:
            instance = ups.pop('instance')
            owner_perm = UserPerm.get(instance, perm)
            owner_perm.update_status(ups['status'])
        for nps in node_perm_status:
            instance = nps.pop('instance')
            owner_perm = instance.owner_perm_cls.get(instance, perm)
            owner_perm.update_status(nps['status'])

        cli = LOG_CLI()
        cli.assign_perm_owners(perm)
        return Response({'user_perm_status': user_perm_status, 'node_perm_status': node_perm_status})


def filter_owner_perms(self, owner_key, cls):
    '''
    查询权限判定结果
    '''
    kwargs = {
        'owner__{}'.format(owner_key): self.kwargs[owner_key],
    }
    subject = self.request.query_params.get('subject', '')
    if subject:
        kwargs.update(perm__subject=subject)

    action_except = self.request.query_params.get('action_except', '')
    if action_except:
        kwargs.update(perm__action_except=action_except)

    action = self.request.query_params.get('action', '')
    if action:
        kwargs.update(perm__action=action)
        kwargs.pop('perm__action_except', '')

    scope = self.request.query_params.get('scope', '')
    if scope:
        kwargs.update(perm__scope=scope)

    if 'perm__action_except' in kwargs:
        action_except = kwargs.pop('perm__action_except')
        queryset = cls.valid_objects.filter(**kwargs).exclude(perm__action=action_except).order_by('perm')
    else:
        queryset = cls.valid_objects.filter(**kwargs).order_by('perm')
    return queryset


class UserPermView(
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        generics.ListCreateAPIView,
):
    """
    用户的权限信息 [GET],[PATCH]
    """
    serializer_class = UserPermResultSerializer
    pagination_class = DefaultListPaginator
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_object(self):
        """
        find user
        """
        user = User.valid_objects.get_queryset().filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        if not user.under_manage(self.request.user):
            raise PermissionDenied
        return user

    def get_queryset(self):
        return filter_owner_perms(self, owner_key='username', cls=UserPerm)

    def patch(self, request, username):    # pylint: disable=unused-argument
        """
        update user perms
        """
        user = self.get_object()
        data = request.data
        perm_statuses = data.get('perm_statuses', []) if data else []

        for perm_status in perm_statuses:
            try:
                perm = Perm.valid_objects.get_queryset().get(uid=perm_status['uid'])
            except ObjectDoesNotExist:
                raise ValidationError({'perm_statuses': ['perm:{} does not exist'.format(perm_status['uid'])]})
            if not perm.under_manage(self.request.user):
                raise ValidationError({'perm_statuses': ['perm:{} out of scope'.format(perm_status['uid'])]})
            user_perm = UserPerm.valid_objects.get_queryset().get(owner=user, perm=perm)

            user_perm.update_status(perm_status['status'])

        res_user_perms = UserPerm.valid_objects.filter(owner=user,
                                                       perm__uid__in=[item['uid'] for item in perm_statuses])
        cli = LOG_CLI()
        cli.assign_user_perms(user)
        return Response(self.get_serializer(res_user_perms, many=True).data)


class UserSelfPermView(generics.ListAPIView):
    '''
    用户自己拥有的权限 [GET]
    只返回拥有的权限
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = UserPermResultSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        filters = {
            'owner__username': self.request.user.username,
            'value': True,
        }
        res = UserPerm.valid_objects.filter(**filters).order_by('perm')
        return res


class GroupPermView(
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        generics.ListCreateAPIView,
):
    """
    组的权限信息 [GET],[PATCH]
    """
    serializer_class = PermResultSerializer
    pagination_class = DefaultListPaginator
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_object(self):
        """
        find group
        """
        group = Group.valid_objects.get_queryset().filter(uid=self.kwargs['uid']).first()
        if not group:
            raise NotFound
        if not group.under_manage(self.request.user):
            raise PermissionDenied
        return group

    def get_queryset(self):
        return filter_owner_perms(self, owner_key='uid', cls=GroupPerm)

    def patch(self, request, uid):    # pylint: disable=unused-argument
        """
        update group perms
        """
        data = request.data
        group = self.get_object()

        perm_statuses = data.get('perm_statuses', []) if data else []

        for perm_status in perm_statuses:
            try:
                perm = Perm.valid_objects.get_queryset().get(uid=perm_status['uid'])
            except ObjectDoesNotExist:
                raise ValidationError({'perm_statuses': ['perm:{} does not exist'.format(perm_status['uid'])]})
            if not perm.under_manage(request.user):
                raise ValidationError({'perm_statuses': ['perm:{} out of scope'.format(perm_status['uid'])]})
            group_perm = GroupPerm.valid_objects.get_queryset().get(owner=group, perm=perm)
            group_perm.update_status(perm_status['status'])

        res_group_perms = GroupPerm.valid_objects.filter(owner=group,
                                                         perm__uid__in=[item['uid'] for item in perm_statuses])
        cli = LOG_CLI()
        cli.assign_node_perms(group)
        return Response(self.get_serializer(res_group_perms, many=True).data)


class DeptPermView(
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        generics.ListCreateAPIView,
):
    """
    部门的权限信息 [GET],[PATCH]
    """
    serializer_class = PermResultSerializer
    pagination_class = DefaultListPaginator
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_object(self):
        """
        find user
        """
        dept = Dept.valid_objects.get_queryset().filter(uid=self.kwargs['uid']).first()
        if not dept:
            raise NotFound
        if not dept.under_manage(self.request.user):
            raise PermissionDenied
        return dept

    def get_queryset(self):
        return filter_owner_perms(self, owner_key='uid', cls=DeptPerm)

    def patch(self, request, uid):    # pylint: disable=unused-argument
        """
        update user perms
        """
        dept = self.get_object()

        perm_statuses = request.data.get('perm_statuses', [])

        for perm_status in perm_statuses:
            try:
                perm = Perm.valid_objects.get_queryset().get(uid=perm_status['uid'])
            except ObjectDoesNotExist:
                raise ValidationError({'perm_statuses': ['perm:{} does not exist'.format(perm_status['uid'])]})
            if not perm.under_manage(request.user):
                raise ValidationError({'perm_statuses': ['perm:{} out of scope'.format(perm_status['uid'])]})
            dept_perm = DeptPerm.valid_objects.get_queryset().get(owner=dept, perm=perm)
            dept_perm = dept_perm.update_status(perm_status['status'])

        res_dept_perms = DeptPerm.valid_objects.filter(owner=dept,
                                                       perm__uid__in=[item['uid'] for item in perm_statuses])
        cli = LOG_CLI()
        cli.assign_node_perms(dept)
        return Response(self.get_serializer(res_dept_perms, many=True).data)


class UserPermListView(generics.GenericAPIView):
    '''
    即刻计算一个用户的权限结果 [PUT]
    '''
    def get_object(self):
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        return user

    def put(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        即刻更新权限结果
        '''
        user = self.get_object()
        task = update_user_perm_in_db.delay(user.id)
        return Response({'task_id': task.task_id, 'task_msg': f'update user:[{user.username}] perms'})


class UserPermDetailView(generics.RetrieveUpdateAPIView):
    '''
    获取一个用户对于某权限的详细信息，包括授权来源 [GET]
    即刻计算权限结果 [PUT]
    '''

    serializer_class = UserPermDetailSerializer
    permission_classes = [IsAuthenticated & (IsAdminUser | IsManagerUser)]

    def get_object(self):
        user_perm = UserPerm.valid_objects.filter(
            owner__username=self.kwargs['username'],
            perm__uid=self.kwargs['perm_uid'],
        ).first()

        if not user_perm:
            raise NotFound

        if not user_perm.owner.under_manage(self.request.user):
            raise PermissionDenied

        if not user_perm.perm.under_manage(self.request.user):
            raise PermissionDenied

        return user_perm

    def put(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        即刻更新权限结果
        '''
        user_perm = self.get_object()
        user = user_perm.owner
        perm = user_perm.perm
        user_perm = user.process_perm_realtime(perm)

        return Response(self.get_serializer(user_perm).data)


class MetaPermAPIView(APIView):
    '''
    获取内置权限基本信息
    '''

    permission_classes = [IsAuthenticated & IsAdminUser]

    def get(self, request):    # pylint: disable=unused-argument, no-self-use
        '''
        获取内置权限
        '''
        data = [
            {
                'uid': 'system_user_create',
                'name': '创建用户',
            },
            {
                'uid': 'system_category_create',
                'name': '创建大类',
            },
            {
                'uid': 'system_app_create',
                'name': '创建应用',
            },
            {
                'uid': 'system_log_read',
                'name': '查看日志',
            },
            {
                'uid': 'system_config_write',
                'name': '公司基本信息配置、基础设施配置',
            },
            {
                'uid': 'system_account_sync',
                'name': '账号同步',
            },
        ]
        return Response(data)
