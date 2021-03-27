from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from rest_framework import serializers

class BaseDynamicFieldModelSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.UUIDField(label='UUID', read_only=True, format='hex')

class AppBaseSerializer(serializers.Serializer):
    
    # protocol_type = serializers.CharField()
    # protocol_data = serializers.JSONField()
    type = serializers.CharField()
    data = serializers.JSONField()

    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    url = serializers.URLField()
    description = serializers.CharField()