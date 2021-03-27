from tenant.models import Tenant
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from drf_spectacular.utils import extend_schema_field

class TenantSerializer(BaseDynamicFieldModelSerializer):
    class Meta:
        model = Tenant

        fields = (
            'uuid',
            'name',
            'slug',
            'icon',
            'created',
        )
