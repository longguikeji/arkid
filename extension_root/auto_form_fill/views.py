from drf_spectacular.utils import extend_schema
from common.code import Code
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.http.response import JsonResponse
from common.paginator import DefaultListPaginator
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from openapi.utils import extend_schema
from extension_root.auto_form_fill.serializers.AppAccountSerializer import AppAccountSerializer
from inventory.models import User
from extension_root.auto_form_fill.models.AppAccount import AppAccount


@extend_schema(roles=['general user', 'tenant admin', 'global admin'], tags=['user'])
class UserAppAccountListView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppAccountSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        user = self.request.user
        result = AppAccount.valid_objects.filter(user=user)
        return result


@extend_schema(roles=['general user', 'tenant admin', 'global admin'], tags=['user'])
class UserAppAccountDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = AppAccountSerializer

    def get_object(self):
        account_uuid = self.kwargs['account_uuid']
        return AppAccount.valid_objects.filter(uuid=account_uuid).first()
