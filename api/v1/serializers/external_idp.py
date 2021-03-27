from rest_framework import serializers
from extension.models import Extension


class ExternalIdpSerializer(serializers.Serializer):

    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
