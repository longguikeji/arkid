from rest_framework import serializers
from system.models import SystemConfig, SystemPrivacyNotice
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from api.v1.fields.custom import (
    create_html_field,
)


class SystemDataConfigSerializer(serializers.Serializer):
    is_open_register = serializers.BooleanField(label=_('是否可以注册用户'))


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


class SystemPrivacyNoticeSerializer(BaseDynamicFieldModelSerializer):
    content = create_html_field(serializers.CharField)(hint=_("隐私声明内容"), required=True)

    class Meta:
        model = SystemPrivacyNotice

        fields = ('title', 'content', 'is_active')

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.content = validated_data.get('content')
        instance.is_active = validated_data.get('is_active')
        instance.save()
        return instance
