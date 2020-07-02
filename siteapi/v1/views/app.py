'''
views about app
'''
# pylint: disable=attribute-defined-outside-init
from urllib.parse import urlparse
import uuid as uuid_utils
import base64

from rest_framework import generics, status
from rest_framework.exceptions import (
    MethodNotAllowed,
    NotFound,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.db import transaction
from django.db.models import Q
from kubernetes import (
    client as k8s_client,
    config as k8s_config,
)

from oneid_meta.models.appgroup import AppGroupMember
from siteapi.v1.serializers.app import (
    APPSerializer,
    APPWithAccessOwnerSerializer,
    APPPublicSerializer,
    OAuthAPPSerializer,
)
from siteapi.v1.views.utils import gen_uid
from siteapi.v1.views.org import validity_check
from common.django.drf.paginator import DefaultListPaginator
from oneid_meta.models import APP, Perm, UserPerm, Dept, User, Group, OAuthAPP    # pylint: disable=ungrouped-imports
from oneid.permissions import (IsAPPManager, IsAdminUser, IsManagerOf, IsOrgOwnerOf, CustomPerm)
from executer.core import CLI
from executer.log.rdb import LOG_CLI


class APPListCreateAPIView(generics.ListCreateAPIView):
    '''
    管理页面-应用列表 [GET], [POST]
    子管理员管理范围内的应用列表
    '''
    pagination_class = DefaultListPaginator

    def get_permissions(self):
        '''
        读写权限
        '''
        self.org = validity_check(self.kwargs['oid'])

        read_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | IsManagerOf(self.org))]
        write_permission_classes = [
            IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | CustomPerm(f'{self.kwargs["oid"]}_app_create'))
        ]

        if self.request.method in SAFE_METHODS:
            return [perm() for perm in read_permission_classes]
        return [perm() for perm in write_permission_classes]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return APPWithAccessOwnerSerializer
        return APPSerializer

    def get_queryset(self):    # pylint: disable=too-many-locals
        '''
        get app list
        '''
        kwargs = {}
        name = self.request.query_params.get('name', '')
        if name:
            kwargs = {'name__icontains': name}

        # 可管理范围
        manager_app_uids = set()
        for manager_group in self.request.user.org_manager_groups(self.org):
            manager_app_uids.update(set(manager_group.apps))
        kwargs['uid__in'] = manager_app_uids
        if self.request.user.is_admin:
            kwargs.pop('uid__in')
            manager_app_uids = None

        # 筛选-对owner可访问
        owner = None
        access_app_uids = None
        node_uid = self.request.query_params.get('node_uid', None)
        if node_uid:
            node, _ = Dept.retrieve_node(node_uid)
            if not node:
                raise ValidationError({'node_uid': ['not found']})
            owner = node
        user_uid = self.request.query_params.get('user_uid', None)
        if user_uid:
            user = User.valid_objects.filter(username=user_uid).first()
            if not user:
                raise ValidationError({'user_uid': ['not found']})
            owner = user

        if owner:
            owner_access = self.request.query_params.get('owner_access', None)
            if owner_access is not None:
                if owner_access in (True, 'true', 'True'):
                    value = True
                elif owner_access in (False, 'false', 'False'):
                    value = False
                else:
                    raise ValidationError({'owner_access': ['must be a boolean']})
                scope_kwargs = {} if manager_app_uids is None else {'perm__scope__in': manager_app_uids}
                access_app_uids = [
                    item['perm__scope'] for item in owner.owner_perm_cls.valid_objects.filter(
                        owner=owner,
                        perm__subject='app',
                        perm__action='access',
                        value=value,
                        **scope_kwargs,
                    ).values('perm__scope')
                ]

                kwargs['uid__in'] = access_app_uids

        apps = APP.valid_objects.filter(**kwargs).exclude(uid='oneid').order_by('-created')
        return apps

    @transaction.atomic()
    def create(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        create app [POST]
        '''
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        app = serializer.instance
        app.owner = self.org
        app.save()
        self._auto_add_default_appgroup(app)
        self._auto_create_access_perm(app)
        self._auto_create_manager_group(request, app)
        if data.get("secret_required", False):
            create_secret_for_app(app)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(serializer.data))

    def perform_create(self, serializer):
        super().perform_create(serializer)    # pylint: disable=no-member
        cli = LOG_CLI()
        cli.create_app(serializer.validated_data, self.org)

    @staticmethod
    def _auto_create_manager_group(request, app):
        '''
        当创建应用时，自动创建子管理员组
        成员只有创建者一人，节点管理范围为空，人员管理范围仅自己，应用管理范围仅此一个应用
        TODO 创建者此时没有获得应用访问权限，可考虑同时获得访问权限
        '''
        cli = CLI()
        data = {
            'uid': gen_uid(name=uuid_utils.uuid4().hex[:6], cls=Group),
            'name': f'管理应用{app.name}',
            'manager_group': {
                'apps': [app.uid],
                'users': [request.user.username],
                'scope_subject': 2,
            }
        }
        manager_group = cli.create_group(data, app.owner)
        cli.add_group_to_group(manager_group, app.owner.manager)
        cli.add_users_to_group([request.user], manager_group)

    @staticmethod
    def _auto_create_access_perm(app):
        '''
        当创建应用时，自动创建访问权限
        '''
        Perm.valid_objects.create(name=f'访问{app.name}', subject='app', scope=app.uid, action='access')

    def _auto_add_default_appgroup(self, app):
        """
        创建应用时，自动加入默认应用分组
        """
        app_group_member = AppGroupMember.valid_objects.create(app=app, owner=self.org.default_app_group)
        app_group_member.order_no = app_group_member.get_max_order_no(owner=self.org.default_app_group)
        app_group_member.save()


class UcenterAPPListAPIView(generics.ListAPIView):
    '''
    用户可见应用列表 [GET]
    有access权限即可见
    '''

    permission_classes = [IsAuthenticated]
    pagination_class = DefaultListPaginator
    serializer_class = APPPublicSerializer

    def get_queryset(self):
        '''
        filter app with access perm
        '''
        kwargs = {}
        name = self.request.query_params.get('name', '')
        if name:
            kwargs['name__icontains'] = name

        uids = [
            item['perm__scope'] for item in UserPerm.valid_objects.filter(
                owner=self.request.user,
                value=True,
                perm__subject='app',
                perm__action__startswith='access',
            ).values('perm__scope')
        ]

        if self.request.user.is_admin:
            return APP.valid_objects.filter(**kwargs).order_by('-created')
        return APP.valid_objects.filter(
            Q(uid__in=uids, owner__in=self.request.user.organizations, allow_any_user=False)
            | Q(allow_any_user=True), **kwargs).order_by('-created')


def create_secret_for_app(app):
    '''
    将client secret以k8s secret形式存储
    deprecated
    TODO:
        - 目前job缺少对完成状况的判断
    '''
    k8s_config.load_kube_config()
    client = k8s_client.CoreV1Api()

    oauth_app = OAuthAPP.objects.filter(app=app).first()

    ark_app_uid = app.uid    # "arker-{arkerPK}"
    if oauth_app:
        secret = k8s_client.V1Secret(
            api_version="v1",
            data={
                "OAUTH_CLIENT_ID": (base64.b64encode(str.encode(oauth_app.client_id))).decode("utf-8"),
                "OAUTH_CLIENT_SECRET": (base64.b64encode(str.encode(oauth_app.client_secret))).decode("utf-8"),
            },
            kind="Secret",
            metadata={
                "name": ark_app_uid,
                "namespace": ark_app_uid,
            },
        )
        thread = client.create_namespaced_secret(namespace=ark_app_uid, body=secret, async_req=True)
        res = thread.get()
        print(res)


class APPDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    指定应用信息 [GET], [PATCH], [DELETE]
    '''
    serializer_class = APPSerializer
    permission_classes = [IsAuthenticated & IsAPPManager]

    def get_object(self):
        '''
        find app
        :rtype: oneid_meta.models.APP
        '''
        app = APP.valid_objects.filter(uid=self.kwargs['uid']).first()
        if not app:
            raise NotFound
        self.check_object_permissions(self.request, app)
        return app

    def perform_destroy(self, instance):
        '''
        reject if not editable
        '''
        if not instance.editable:
            raise MethodNotAllowed('DELETE protected APP')
        cli = LOG_CLI()
        cli.delete_app(instance)
        instance.delete()

    def perform_update(self, serializer):
        super().perform_update(serializer)    # pylint: disable=no-member
        cli = LOG_CLI()
        cli.update_app(serializer.instance, serializer.validated_data)


class APPOAuthRegisterAPIView(generics.CreateAPIView):
    '''
    若此 app 不存在则创建，存在则更新
    目前此处限制 client 类型，只允许配置 redirect_uris
    '''
    serializer_class = OAuthAPPSerializer
    permission_classes = [IsAuthenticated & (IsAdminUser)]

    def get_object(self):
        '''
        find app
        allow None
        '''
        return APP.valid_objects.filter(uid=self.kwargs['uid']).first()

    def create(self, request, uid, **kwargs):    # pylint: disable=arguments-differ
        '''
        [POST] 实际扮演 [POST] 或 [PATCH]
        '''
        app = self.get_object()
        redirect_uris = request.data.get('redirect_uris', '')
        parsed_uri = urlparse(redirect_uris)
        index = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        if not redirect_uris:
            raise ValidationError({'redirect_uris': ['required']})
        if app:
            app.index = index
            app.save()
            oauth_app = OAuthAPP.objects.filter(app=app).first()
            if oauth_app:
                oauth_app.redirect_uris = redirect_uris
                oauth_app.save()
            else:
                oauth_app = OAuthAPP.objects.create(redirect_uris=redirect_uris, app=app)
            return Response(self.get_serializer(oauth_app).data)

        app = APP.valid_objects.create(uid=uid, name=uid, index=index)
        oauth_app = OAuthAPP.objects.create(redirect_uris=redirect_uris, app=app)
        return Response(self.get_serializer(oauth_app).data, status=status.HTTP_201_CREATED)
