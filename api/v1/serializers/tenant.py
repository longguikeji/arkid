from tenant.models import Tenant, TenantConfig
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Permission
from api.v1.fields.custom import (
    create_enum_field,
)

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

    def create(self, validated_data):
        tenant = Tenant.objects.create(
            **validated_data
        )
        user = self.context['request'].user
        if user and user.username != "":
            user.tenants.add(tenant)
        permission = Permission.active_objects.filter(codename=tenant.admin_perm_code).first()
        if permission:
            user.user_permissions.add(permission)
        return tenant


class MobileLoginRequestSerializer(serializers.Serializer):

    mobile = serializers.CharField(label=_('手机号'))
    code = serializers.CharField(label=_('验证码'))


class MobileLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
    has_tenant_admin_perm = serializers.ListField(child=serializers.CharField(), label=_('权限列表'))


class MobileRegisterRequestSerializer(serializers.Serializer):

    mobile = serializers.CharField(label=_('手机号'))
    code = serializers.CharField(label=_('验证码'))
    password = serializers.CharField(label=_('密码'))


class MobileRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class UserNameRegisterRequestSerializer(serializers.Serializer):

    username = serializers.CharField(label=_('用户名'))
    password = serializers.CharField(label=_('密码'))


class UserNameLoginRequestSerializer(serializers.Serializer):

    username = serializers.CharField(label=_('用户名'))
    password = serializers.CharField(label=_('密码'))
    code = serializers.CharField(label=_('图片验证码'), required=False)
    code_filename = serializers.CharField(label=_('图片验证码的文件名称'), required=False)


class UserNameRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class UserNameLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
    has_tenant_admin_perm = serializers.ListField(child=serializers.CharField(), label=_('权限列表'))


class ConfigSerializer(serializers.Serializer):
    is_open_authcode = serializers.BooleanField(label=_('是否打开验证码'))
    error_number_open_authcode = serializers.IntegerField(label=_('错误几次提示输入验证码'))
    is_open_register_limit = serializers.BooleanField(label=_('是否限制注册用户'))
    register_time_limit = serializers.IntegerField(label=_('用户注册时间限制(分钟)'))
    register_count_limit = serializers.IntegerField(label=_('用户注册数量限制'))
    upload_file_format = serializers.ListField(child=serializers.CharField(), label=_('允许上传的文件格式'))

    mobile_login_register_enabled = serializers.BooleanField(label=_('开启手机号登录注册'))
    secret_login_register_enabled = serializers.BooleanField(label=_('开启密码登录注册'))
    secret_login_register_field_names = serializers.ListField(child=serializers.CharField(), label=_('用于密码登录的基础字段'))

    custom_login_register_field_uuids = serializers.ListField(child=serializers.CharField(), label=_('用于登录的自定义字段UUID'))
    custom_login_register_enabled = serializers.BooleanField(label=_('开启自定义字段登录注册'))

    need_complete_profile_after_register = serializers.BooleanField(label=_('注册完成后跳转到完善用户资料页面'))
    can_skip_complete_profile = serializers.BooleanField(label=_('完善用户资料页面允许跳过'))



class TenantConfigSerializer(BaseDynamicFieldModelSerializer):

    data = ConfigSerializer()

    class Meta:
        model = TenantConfig

        fields = (
            'data',
        )

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = data
        instance.save()
        return instance
