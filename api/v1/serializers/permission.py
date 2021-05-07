from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from inventory.models import Permission
from rest_framework import serializers

class PermissionSerializer(DynamicFieldsModelSerializer):

    uuid = serializers.CharField(read_only=True)
    codename = serializers.CharField(read_only=True)

    class Meta:
        model = Permission

        fields = (
            'uuid',
            'name',
            'codename',
        )
