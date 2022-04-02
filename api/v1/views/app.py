import jwt
import json
from .base import BaseViewSet
from common.code import Code
from rest_framework.response import Response

from app.models import App
from api.v1.serializers.app import (
    AppSerializer,
    AppListSerializer,
    AppProvisioningSerializer,
    AppProvisioningMappingSerializer,
    AppProvisioningProfileSerializer,
    AddAuthTmplSerializer,
    AppNewListSerializer,
)
from common.paginator import DefaultListPaginator
from django.http.response import JsonResponse
from rest_framework.views import APIView
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from runtime import get_app_runtime
from provisioning.models import Config
from inventory.models import Permission, UserAppPermissionResult
from schema.models import Schema, AppProfile
from rest_framework.decorators import action
from oauth2_provider.models import Application
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from drf_spectacular.utils import OpenApiParameter
from perm.custom_access import ApiAccessPermission
from django.utils.translation import gettext_lazy as _
from common.code import Code
from webhook.manager import WebhookManager
from django.db import transaction
from rest_framework import generics
from tenant.models import Tenant

AppPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='AppPolymorphicProxySerializer',
    serializers=get_app_runtime().app_type_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    list=extend_schema(
        roles=['tenantadmin', 'globaladmin', 'appmanage'],
        parameters=[
            OpenApiParameter(
                name='name',
                type={'type': 'string'},
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ],
    ),
)
@extend_schema(
    tags=['app'],
)
class AppViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        name = self.request.query_params.get('name', None)
        kwargs = {
        }
        tenant = context['tenant']

        if name is not None:
            kwargs['name'] = name
        qs = App.active_objects.filter(tenant=tenant).filter(**kwargs).order_by('id')
        return qs

    def get_object(self):
        uuid = self.kwargs['pk']
        context = self.get_serializer_context()
        tenant = context['tenant']

        return (
            App.active_objects.filter(
                tenant=tenant,
                uuid=uuid,
            )
            .order_by('id')
            .first()
        )

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'appmanage'],
        summary='租户app删除'
    )
    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        app = self.get_object()
        ret = super().destroy(request, *args, **kwargs)
        transaction.on_commit(lambda: WebhookManager.app_deleted(tenant.uuid, app))
        return ret

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'appmanage'],
        summary='租户app列表'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'appmanage'],
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
        summary='租户app修改'
    )
    def update(self, request, *args, **kwargs):
        data = request.data.get('data', '')
        if data:
            redirect_uris = data.get('redirect_uris', '')
            if redirect_uris:
                if redirect_uris.startswith('http') or redirect_uris.startswith(
                    'https'
                ):
                    pass
                else:
                    return JsonResponse(
                        data={
                            'error': Code.URI_FROMAT_ERROR.value,
                            'message': _('redirect_uris format error'),
                        }
                    )
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'appmanage'],
        request=AppPolymorphicProxySerializer,
        responses=AppPolymorphicProxySerializer,
        summary='租户app创建',
    )
    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()

        data = request.data.get('data', '')
        if data:
            redirect_uris = data.get('redirect_uris', '')
            if redirect_uris:
                if redirect_uris.startswith('http') or redirect_uris.startswith(
                    'https'
                ):
                    pass
                else:
                    return JsonResponse(
                        data={
                            'error': Code.URI_FROMAT_ERROR.value,
                            'message': _('redirect_uris format error'),
                        }
                    )
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser', 'appmanage'],
        responses=AppPolymorphicProxySerializer, summary='租户app获取'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'], 
        request=AddAuthTmplSerializer,
        responses=AddAuthTmplSerializer,
        summary='租户app添加auth_tmpl'
    )
    @action(detail=True, methods=['post'])
    def add_auth_tmpl(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        app_uuid = self.kwargs['pk']
        app = App.active_objects.filter(tenant=tenant, uuid=app_uuid).first()
        tmpl = request.data.get('html')

        if not app:
            return {'error': Code.ADD_AUTH_TMPL_ERROR, 'message': 'No app found'}
        app.auth_tmpl = tmpl
        app.save()

        auth_app = Application.objects.filter(name=app.id).first()
        if not auth_app:
            return {'error': Code.ADD_AUTH_TMPL_ERROR, 'message': 'No oauth app found'}
        auth_app.custom_template = tmpl
        auth_app.save()
        return Response({'error': Code.OK.value})


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['app'])
class AppProvisioningView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = AppProvisioningSerializer

    def get_object(self):
        app_uuid = self.kwargs['app_uuid']
        tenant_uuid = self.kwargs['tenant_uuid']
        app = App.objects.filter(uuid=app_uuid, tenant__uuid=tenant_uuid).first()
        config, is_created = Config.valid_objects.get_or_create(app=app)
        return config

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='app配置获取'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='app配置更新'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='app配置修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['app'])
class AppProvisioningMappingView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppProvisioningMappingSerializer

    def get_queryset(self):
        app_uuid = self.kwargs['app_uuid']
        tenant_uuid = self.kwargs['tenant_uuid']
        app = App.objects.filter(uuid=app_uuid, tenant__uuid=tenant_uuid).first()
        config = Config.valid_objects.filter(app=app).first()
        mapping = Schema.active_objects.filter(
            provisioning_config=config,
        )
        return mapping


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['app'])
class AppProvisioningMappingDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppProvisioningMappingSerializer

    def get_object(self):
        app_uuid = self.kwargs['app_uuid']
        tenant_uuid = self.kwargs['tenant_uuid']
        app = App.objects.filter(uuid=app_uuid, tenant__uuid=tenant_uuid).first()
        config = Config.valid_objects.filter(app=app).first()
        map_uuid = self.kwargs['map_uuid']
        map = Schema.active_objects.filter(
            uuid=map_uuid, provisioning_config=config
        ).first()
        return map

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='应用权限mapping详情'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='应用权限mapping修改'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='应用权限mapping修改'
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='应用权限mapping删除'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['app'])
class AppProvisioningProfileView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppProvisioningProfileSerializer

    def get_queryset(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        app_uuid = self.kwargs['app_uuid']
        app = App.objects.filter(uuid=app_uuid, tenant__uuid=tenant_uuid).first()
        config = Config.valid_objects.filter(app=app).first()
        profile = AppProfile.active_objects.filter(
            provisioning_config=config,
        )
        return profile

    @extend_schema(summary='app配置信息列表', roles=['tenantadmin', 'globaladmin'])
    def get(self, request, *args, **kwargs):
        return super(AppProvisioningProfileView, self).get(request, *args, **kwargs)

    @extend_schema(summary='app配置信息创建', roles=['tenantadmin', 'globaladmin'])
    def post(self, request, *args, **kwargs):
        return super(AppProvisioningProfileView, self).post(request, *args, **kwargs)


@extend_schema(roles=['tenantadmin', 'globaladmin'], tags=['app'])
class AppProvisioningProfileDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppProvisioningProfileSerializer

    def get_object(self):
        app_uuid = self.kwargs['app_uuid']
        tenant_uuid = self.kwargs['tenant_uuid']
        app = App.objects.filter(uuid=app_uuid, tenant__uuid=tenant_uuid).first()
        config = Config.valid_objects.filter(app=app).first()
        profile_uuid = self.kwargs['profile_uuid']
        profile = AppProfile.active_objects.filter(
            uuid=profile_uuid, provisioning_config=config
        ).first()
        return profile
    
    @extend_schema(summary='app配置详情获取', roles=['tenantadmin', 'globaladmin'])
    def get(self, request, *args, **kwargs):
        return super(AppProvisioningProfileDetailView, self).get(request, *args, **kwargs)
    
    @extend_schema(summary='app配置详情修改', roles=['tenantadmin', 'globaladmin'])
    def put(self, request, *args, **kwargs):
        return super(AppProvisioningProfileDetailView, self).put(request, *args, **kwargs)
    
    @extend_schema(summary='app配置详情修改', roles=['tenantadmin', 'globaladmin'])
    def patch(self, request, *args, **kwargs):
        return super(AppProvisioningProfileDetailView, self).patch(request, *args, **kwargs)
    
    @extend_schema(summary='app配置详情删除', roles=['tenantadmin', 'globaladmin'])
    def delete(self, request, *args, **kwargs):
        return super(AppProvisioningProfileDetailView, self).delete(request, *args, **kwargs)


@extend_schema(
    roles=['tenantadmin', 'globaladmin', 'authmanage.permissionmanage'],
    tags=['app'],
    summary='租户app列表'
)
class AppListAPIView(generics.ListAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppNewListSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        tenant_uuid = self.kwargs['tenant_uuid']

        kwargs = {
            'tenant__uuid': tenant_uuid,
        }

        qs = App.active_objects.filter(**kwargs).order_by('id')
        return qs


@extend_schema(roles=['tenantadmin', 'globaladmin', 'generaluser'], tags=['tenant'])
class AppPermissionCheckView(APIView):

    permission_classes = []
    authentication_classes = []

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'generaluser'],
        summary='权限鉴定'
    )
    def get(self, request):
        id_token = request.META.get('HTTP_ID_TOKEN', '')
        payload = self.id_token_reverse(id_token)
        client_id = payload.get('aud', None)
        user_uuid = payload.get('sub_uuid', '')
        tenant_uuid = payload.get('tenant_uuid', '')
        # user_uuid = 'c59b055f-726b-4ba4-b550-15c0c69a680e'
        # tenant_uuid = '3efed4d9-f2ee-455e-b868-6f60ea8fdff6'
        # client_id = 'NuLbozhXNrMFYpkhKZlfaf724OaoQSSYlACGE5rF'
        # 存在性判断
        if client_id is None:
            return JsonResponse(data={'error_code': Code.CLIENT_ID_ERROR.value, 'error_msg': 'client_id not exists'})
        if tenant_uuid is None:
            return JsonResponse(data={'error_code': Code.TENANT_NO_EXISTS.value, 'error_msg': 'tenant not exists'})
        if user_uuid is None:
            return JsonResponse(data={'error_code': Code.USER_EXISTS_ERROR.value, 'error_msg': 'user not exists'})
        # 准备数据
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        # TODO 后面这里可以改为筛选所有app
        apps = App.valid_objects.filter(
            type__in=['OIDC-Platform'],
            tenant=tenant,
        )
        app_temp = None
        for app in apps:
            data = app.data
            app_client_id = data.get('client_id', '')
            if app_client_id == client_id:
                app_temp = app
                break
        userappp_permission = UserAppPermissionResult.valid_objects.filter(
            tenant=tenant,
            user__uuid=user_uuid,
            app=app_temp,
        ).first()
        if userappp_permission:
            return JsonResponse(data={'error': Code.OK.value, 'result': userappp_permission.result, 'error_msg': 'request success'})
        else:
            return JsonResponse(data={'error': Code.USER_PERMISSION_EXISTS_ERROR.value, 'error_msg': 'user permission not exists'})
    
    def id_token_reverse(self, id_token):
        try:
            payload = jwt.decode(id_token, options={"verify_signature": False})
            return payload
        except Exception:
            raise Exception("unable to parse id_token")