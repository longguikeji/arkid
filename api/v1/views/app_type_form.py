from rest_framework.fields import JSONField
from external_idp.models import ExternalIdp
import runtime
from .base import BaseViewSet
from rest_framework import viewsets
from extension.models import Extension
from api.v1.serializers.external_idp import ExternalIdpSerializer
from rest_framework.decorators import action
from runtime import get_app_runtime
from django.http.response import JsonResponse
from drf_spectacular.utils import extend_schema
from common.form import AppTypeForm

@extend_schema(
    tags = ['appTypeForm']
)
class AppTypeFormViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ExternalIdpSerializer

    def get_queryset(self):
        r = get_app_runtime()
        objs = r.app_type_forms
        return objs

    def get_object(self):
        r = get_app_runtime()

        form: AppTypeForm
        for key, form in enumerate(r.app_type_forms):
            if key == self.kwargs['pk']:
                return form

        return None