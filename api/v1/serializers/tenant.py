from rest_framework.exceptions import ValidationError
from tenant.models import (
    Tenant,
    TenantConfig,
    TenantPasswordComplexity,
    TenantPrivacyNotice,
)
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Permission
from api.v1.fields.custom import (
    create_enum_field,
    create_upload_url_field,
    create_html_field,
)


class TenantSerializer(BaseDynamicFieldModelSerializer):

    icon = create_upload_url_field(serializers.URLField)(
        hint=_("请选择图标"), required=False
    )

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
        tenant = Tenant.objects.create(**validated_data)
        user = self.context['request'].user
        if user and user.username != "":
            user.tenants.add(tenant)
        permission = Permission.active_objects.filter(
            codename=tenant.admin_perm_code
        ).first()
        if permission:
            user.user_permissions.add(permission)
        TenantPasswordComplexity.active_objects.get_or_create(
            is_apply=True,
            tenant=tenant,
            title='6-18位字母、数字、特殊字符组合',
            regular='^(?=.*[A-Za-z])(?=.*\d)(?=.*[~$@$!%*#?&])[A-Za-z\d~$@$!%*#?&]{6,18}$',
        )
        return tenant


class TenantExtendSerializer(BaseDynamicFieldModelSerializer):
    class Meta:
        model = Tenant

        fields = (
            'uuid',
            'name',
            'slug',
            'icon',
            'created',
            'password_complexity',
        )


class MobileLoginRequestSerializer(serializers.Serializer):

    mobile = serializers.CharField(label=_('手机号'))
    code = serializers.CharField(label=_('验证码'))


class MobileLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
    has_tenant_admin_perm = serializers.ListField(
        child=serializers.CharField(), label=_('权限列表')
    )


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
    has_tenant_admin_perm = serializers.ListField(
        child=serializers.CharField(), label=_('权限列表')
    )


class ConfigSerializer(serializers.Serializer):
    is_open_authcode = serializers.BooleanField(label=_('是否打开验证码'))
    error_number_open_authcode = serializers.IntegerField(label=_('错误几次提示输入验证码'))
    is_open_register_limit = serializers.BooleanField(label=_('是否限制注册用户'))
    register_time_limit = serializers.IntegerField(label=_('用户注册时间限制(分钟)'))
    register_count_limit = serializers.IntegerField(label=_('用户注册数量限制'))
    upload_file_format = serializers.ListField(
        child=serializers.CharField(), label=_('允许上传的文件格式')
    )
    close_page_auto_logout = serializers.BooleanField(label=_('是否关闭页面自动退出'))

    native_login_register_field_names = serializers.ListField(
        child=serializers.CharField(), label=_('用于密码登录的基础字段')
    )

    custom_login_register_field_uuids = serializers.ListField(
        child=serializers.CharField(), label=_('用于登录的自定义字段UUID')
    )
    custom_login_register_field_names = serializers.ListField(
        child=serializers.CharField(), label=_('用于登录的自定义字段名称')
    )

    need_complete_profile_after_register = serializers.BooleanField(
        label=_('注册完成后跳转到完善用户资料页面')
    )
    can_skip_complete_profile = serializers.BooleanField(label=_('完善用户资料页面允许跳过'))


class TenantConfigSerializer(BaseDynamicFieldModelSerializer):

    data = ConfigSerializer()

    class Meta:
        model = TenantConfig

        fields = ('data',)

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = data
        instance.save()
        return instance


class TenantPasswordComplexitySerializer(BaseDynamicFieldModelSerializer):
    regular = serializers.CharField(label=_('正则表达式'))
    is_apply = serializers.BooleanField(label=_('是否应用'))
    title = serializers.CharField(label=_('标题'))

    class Meta:
        model = TenantPasswordComplexity

        fields = (
            'uuid',
            'regular',
            'is_apply',
            'title',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
        }

    def create(self, validated_data):
        tenant_uuid = (
            self.context['request'].parser_context.get('kwargs').get('tenant_uuid')
        )
        regular = validated_data.get('regular')
        is_apply = validated_data.get('is_apply')
        title = validated_data.get('title')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        complexity = TenantPasswordComplexity()
        complexity.tenant = tenant
        complexity.regular = regular
        complexity.is_apply = is_apply
        complexity.title = title
        complexity.save()
        if is_apply is True:
            TenantPasswordComplexity.active_objects.filter(tenant=tenant).exclude(
                id=complexity.id
            ).update(is_apply=False)
        return complexity

    def update(self, instance, validated_data):
        tenant_uuid = (
            self.context['request'].parser_context.get('kwargs').get('tenant_uuid')
        )
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        is_apply = validated_data.get('is_apply')
        if is_apply is True:
            TenantPasswordComplexity.active_objects.filter(tenant=tenant).exclude(
                id=instance.id
            ).update(is_apply=False)
        instance.__dict__.update(validated_data)
        instance.save()
        return instance


class TenantPrivacyNoticeSerializer(BaseDynamicFieldModelSerializer):
    content = create_html_field(serializers.CharField)(hint=_("隐私声明内容"))

    class Meta:
        model = TenantPrivacyNotice

        fields = ('title', 'content', 'is_active')

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.content = validated_data.get('content')
        instance.is_active = validated_data.get('is_active')
        instance.save()
        return instance
