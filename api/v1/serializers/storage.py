from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field


class UploadSerializer(serializers.Serializer):

    file = serializers.FileField(write_only=True)
    key = serializers.CharField(read_only=True)

    class Meta:

        fields = (
            'key',
        )