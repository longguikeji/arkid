from requestlogs.storages import BaseEntrySerializer
from rest_framework import serializers


class CustomEntrySerializer(BaseEntrySerializer):
    class TenantSerializer(serializers.Serializer):
        uuid = serializers.CharField()
        name = serializers.CharField()
        slug = serializers.CharField()

    class UserSerializer(serializers.Serializer):
        uuid = serializers.CharField()
        username = serializers.CharField()
        admin = serializers.BooleanField()

    tenant = TenantSerializer()
    user = UserSerializer()
    host = serializers.CharField()
