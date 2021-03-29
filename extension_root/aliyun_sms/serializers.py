from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class AliyunSMSConfigSerializer(serializers.Serializer):

    access_key = serializers.CharField(required=True, label=_('Access Key'))
    secret_key = serializers.CharField(required=True, label=_('Secret Key'))
    template = serializers.CharField(required=True, label=_('Template'))
    signature = serializers.CharField(required=True, label=_('Signature'))


class AliyunSMSSerializer(serializers.Serializer):
    
    data = AliyunSMSConfigSerializer(label=_('data'))
    