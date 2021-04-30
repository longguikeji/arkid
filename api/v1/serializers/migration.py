from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field


class MigrationSerializer(serializers.Serializer):
    tenant_uuid = serializers.CharField(write_only=True)
    error = serializers.CharField(read_only=True)

    class Meta:

        fields = ('tenant_uuid', 'error')
