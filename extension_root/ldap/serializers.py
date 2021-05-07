from rest_framework import serializers
from oauth2_provider.models import Application
from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer
from runtime import get_app_runtime


class LDAPConfigSerializer(serializers.Serializer):
    
    base_dn = serializers.CharField(default="dc=example,dc=org")


class LDAPAppSerializer(AppBaseSerializer):

    data = LDAPConfigSerializer()
