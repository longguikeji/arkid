from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import LoginRegisterConfigBaseSerializer
from api.v1.fields.custom import create_password_field


class MobileLoginRegisterConfigDataSerializer(serializers.Serializer):

    login_enabled = serializers.BooleanField(default=True, label=_('启用登录'))
    register_enabled = serializers.BooleanField(default=True, label=_('启用注册'))
    reset_password_enabled = serializers.BooleanField(
        default=True, label=_('启用通过手机短信重置密码')
    )
    is_open_register_limit = serializers.BooleanField(default=False, label=('是否限制注册用户'))
    register_time_limit = serializers.IntegerField(default=1, label=_('用户注册时间限制(分钟)'))
    register_count_limit = serializers.IntegerField(default=10, label=_('用户注册数量限制'))


class MobileLoginRegisterConfigSerializer(LoginRegisterConfigBaseSerializer):

    data = MobileLoginRegisterConfigDataSerializer(label=_('配置数据'))


class MobileLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
    has_tenant_admin_perm = serializers.ListField(
        child=serializers.CharField(), label=_('权限列表')
    )


class MobileRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class MobileResetPasswordRequestSerializer(serializers.Serializer):

    mobile = serializers.CharField(label=_('手机号'), required=True)
    password = create_password_field(serializers.CharField)(
        label=_('新密码'),
        hint="密码长度大于等于8位的字母数字组合",
        write_only=True,
        required=True,
    )
    check_password = create_password_field(serializers.CharField)(
        label=_('确认密码'),
        hint="密码长度大于等于8位的字母数字组合",
        write_only=True,
        required=True,
    )
    code = serializers.CharField(label=_('验证码'), required=True)


class PasswordSerializer(serializers.Serializer):

    is_succeed = serializers.BooleanField(label=_('是否修改成功'))
