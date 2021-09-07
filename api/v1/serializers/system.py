from rest_framework import serializers
from system.models import SystemConfig
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from api.v1.fields.custom import (
    create_html_field,
)


class SystemDataConfigSerializer(serializers.Serializer):
    is_open_register = serializers.BooleanField(label=_('是否可以注册用户'), default=True)
    password_validity_period = serializers.IntegerField(label=_('密码有效期(天)'), default=60)


class SystemConfigSerializer(BaseDynamicFieldModelSerializer):

    data = SystemDataConfigSerializer()

    class Meta:
        model = SystemConfig

        fields = ('data',)

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = data
        instance.save()
        return instance
