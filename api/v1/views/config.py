#!/usr/bin/env python3
from rest_framework.exceptions import NotFound
from rest_framework import generics
from inventory.models import CustomField, NativeField
from .base import BaseViewSet
from api.v1.serializers.config import (
    CustomFieldSerailizer,
    NativeFieldSerializer,
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from drf_spectacular.utils import extend_schema_view, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.http.response import JsonResponse
from common.code import Code
from django.utils.translation import gettext_lazy as _
from api.v1.serializers.config import (
    PrivacyNoticeSerializer,
    PasswordComplexitySerializer,
)
from tenant.models import Tenant
from config.models import PrivacyNotice, PasswordComplexity
from rest_framework.response import Response
from runtime import get_app_runtime


@extend_schema(
    tags=['tenant_config'],
    roles=['general user', 'tenant admin', 'global admin'],
    parameters=[
        OpenApiParameter(
            name='subject',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class CustomFieldViewSet(BaseViewSet):
    model = CustomField
    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = CustomFieldSerailizer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        subject = self.request.query_params.get('subject', None)

        kwargs = {
            'tenant': tenant,
        }

        if subject is not None:
            kwargs['subject__in'] = subject.split(',')

        qs = CustomField.valid_objects.filter(**kwargs).order_by('id')
        return qs

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        return CustomField.valid_objects.filter(**kwargs).first()

    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        subject = request.query_params.get('subject')
        if subject not in ('user', 'group'):
            return JsonResponse(
                data={
                    'error': Code.QUERY_PARAM_ERROR.value,
                    'message': _('Wrong query param subject'),
                }
            )
        name = request.data.get('name')
        is_duplicate = CustomField.valid_objects.filter(
            tenant=tenant, subject=subject, name=name
        ).exists()
        if is_duplicate:
            return JsonResponse(
                data={
                    'error': Code.DUPLICATED_RECORD_ERROR.value,
                    'message': _('Duplicated custom field found'),
                }
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        subject = request.query_params.get('subject')
        if subject not in ('user', 'group'):
            return JsonResponse(
                data={
                    'error': Code.QUERY_PARAM_ERROR.value,
                    'message': _('Wrong query param subject'),
                }
            )
        name = request.data.get('name')
        is_duplicate = (
            CustomField.valid_objects.filter(tenant=tenant, subject=subject, name=name)
            .exclude(uuid=kwargs.get('pk'))
            .exists()
        )
        if is_duplicate:
            return JsonResponse(
                data={
                    'error': Code.DUPLICATED_RECORD_ERROR.value,
                    'message': _('Duplicated custom field found'),
                }
            )
        return super().update(request, *args, **kwargs)


@extend_schema(
    tags=['system_config'],
    roles=['general user', 'tenant admin', 'global admin'],
)
class NativeFieldListAPIView(generics.ListAPIView):
    '''
    原生字段，不分页
    '''

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = NativeFieldSerializer

    def get_queryset(self):
        '''
        filter the fields
        '''
        return NativeField.valid_objects.all().order_by('name')


@extend_schema(
    tags=['system_config'],
    roles=['general user', 'tenant admin', 'global admin'],
)
class NativeFieldDetailAPIView(generics.RetrieveUpdateAPIView):
    '''
    某原生字段
    '''

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = NativeFieldSerializer

    def get_object(self):
        '''
        filter the field
        '''
        field = NativeField.valid_objects.filter(uuid=self.kwargs['uuid']).first()
        if not field:
            raise NotFound
        return field


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['config'],
    parameters=[
        OpenApiParameter(
            name='tenant',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class PrivacyNoticeView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = PrivacyNoticeSerializer

    def get_object(self):
        # tenant_uuid = self.request.query_params.get('tenant')
        # if not tenant_uuid:
        #     tenant = None
        # else:
        #     tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        # privacy_notice, is_created = PrivacyNotice.objects.get_or_create(
        #     is_del=False, tenant=tenant
        # )
        # return privacy_notice
        r = get_app_runtime()
        privacy_notice_provider = r.privacy_notice_provider
        assert privacy_notice_provider is not None
        return privacy_notice_provider.load_privacy(self.request)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PrivacyNoticeSerializer(instance, data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['config'],
    parameters=[
        OpenApiParameter(
            name='tenant',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class PasswordComplexityView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PasswordComplexitySerializer

    def get_queryset(self):
        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        return PasswordComplexity.active_objects.filter(tenant=tenant).order_by(
            '-is_apply'
        )


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['config'],
    parameters=[
        OpenApiParameter(
            name='tenant',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class PasswordComplexityDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = PasswordComplexitySerializer

    def get_object(self):
        uuid = self.kwargs['complexity_uuid']
        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        return PasswordComplexity.active_objects.filter(
            uuid=uuid, tenant=tenant
        ).first()


@extend_schema(
    roles=['general user', 'tenant admin', 'global admin'],
    tags=['config'],
    parameters=[
        OpenApiParameter(
            name='tenant',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class CurrentPasswordComplexityView(generics.RetrieveAPIView):

    permission_classes = []
    authentication_classes = []

    serializer_class = PasswordComplexitySerializer

    def get_object(self):
        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        return PasswordComplexity.active_objects.filter(
            tenant=tenant, is_apply=True
        ).first()

    def get(self, request):
        comlexity = self.get_object()
        if comlexity:
            serializer = self.get_serializer(comlexity)
            return Response(serializer.data)
        else:
            return Response({})
