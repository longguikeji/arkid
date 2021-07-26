from rest_framework import serializers
from system.models import SystemConfig
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer


class SystemConfigBaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        instance = validated_data.pop('instance')
        subject = validated_data.pop('subject')
        # 去掉validated_data包含具有默认值的key
        tmpl_data = validated_data.copy()
        for key, value in validated_data.items():
            if key not in self.initial_data:
                tmpl_data.pop(key)
        data = instance.data.get(subject)
        if not data:
            instance.data[subject] = tmpl_data
        else:
            data.update(tmpl_data)
        instance.save()
        return instance


class LoginRegisterConfigSerializer(SystemConfigBaseSerializer):
    is_open_register = serializers.BooleanField(label=_('是否可以注册用户'), default=True)


class PrivacyNoticeConfigSerializer(SystemConfigBaseSerializer):
    content = serializers.CharField(label=_('隐私声明的内容'), default='')


class SystemConfigDataSerializer(serializers.Serializer):
    login_register = LoginRegisterConfigSerializer(default={})
    privacy_notice = PrivacyNoticeConfigSerializer(default={})


class SystemConfigSerializer(BaseDynamicFieldModelSerializer):

    data = SystemConfigDataSerializer()

    class Meta:
        model = SystemConfig

        fields = ('data',)

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = data
        instance.save()
        return instance
