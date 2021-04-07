from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from rest_framework import serializers


class BaseDynamicFieldModelSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.UUIDField(label='UUID', read_only=True, format='hex')


class AppBaseSerializer(serializers.Serializer):

    type = serializers.CharField()
    data = serializers.JSONField()

    uuid = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    url = serializers.URLField()
    description = serializers.CharField()


class ExternalIdpBaseSerializer(serializers.Serializer):

    # order_no = serializers.IntegerField()
    type = serializers.CharField()
    data = serializers.JSONField()

    uuid = serializers.UUIDField(read_only=True)


class ExtensionBaseSerializer(serializers.Serializer):

    type = serializers.CharField()
    data = serializers.JSONField()
    uuid = serializers.UUIDField(read_only=True)
