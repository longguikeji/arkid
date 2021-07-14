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
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema(
    tags=['config'],
)
class CustomFieldViewSet(BaseViewSet):
    model = CustomField
    permission_classes = []
    authentication_classes = []

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


@extend_schema(
    tags=['config'],
)
class NativeFieldListAPIView(generics.ListAPIView):
    '''
    原生字段，不分页
    '''
    permission_classes = []
    authentication_classes = []
    serializer_class = NativeFieldSerializer

    def get_queryset(self):
        '''
        filter the fields
        '''
        return NativeField.valid_objects.all().order_by('name')


@extend_schema(
    tags=['config'],
)
class NativeFieldDetailAPIView(generics.RetrieveUpdateAPIView):
    '''
    某原生字段
    '''
    permission_classes = []
    authentication_classes = []
    serializer_class = NativeFieldSerializer

    def get_object(self):
        '''
        filter the field
        '''
        field = NativeField.valid_objects.filter(uuid=self.kwargs['uuid']).first()
        if not field:
            raise NotFound
        return field
