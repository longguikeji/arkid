
from common.serializer import BaseDynamicFieldModelSerializer
from backend_login.models import BackendLogin 
from common.provider import ExternalIdpProvider
from rest_framework import serializers
from django.db.models import Max


class BackendLoginSerializer(BaseDynamicFieldModelSerializer):

    class Meta:

        model = BackendLogin

        fields = (
            'uuid',
            'type',
            'data',
            'order_no',
        )

    def create(self, validated_data):
        from runtime import get_app_runtime, Runtime

        tenant = self.context['tenant']

        backend_login_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        backend_login = BackendLogin.valid_objects.create(
            tenant=tenant,
            type=backend_login_type,
            data = data
        )

        max_order_no = (
            BackendLogin.objects.filter(tenant=tenant)
            .aggregate(Max('order_no'))
            .get('order_no__max')
        )
        backend_login.order_no = max_order_no + 1
        backend_login.save()
        return backend_login

    def update(self, instance, validated_data):
        backend_login_type = validated_data.pop('type')
        data = validated_data.pop('data', None)

        instance.data = data
        instance.type = backend_login_type
        instance.save()
        return instance


class BackendLoginListSerializer(BackendLoginSerializer):
    class Meta:
        model = BackendLogin 

        fields = (
            'type',
            'order_no',
        )


class BackendLoginReorderSerializer(serializers.Serializer):

    backend_logins = serializers.ListField(child=serializers.CharField(), write_only=True)

    error = serializers.CharField(read_only=True)
