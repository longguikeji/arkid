from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import LoginRegisterConfigBaseSerializer
from api.v1.fields.custom import create_password_field


class PasswordLoginRegisterConfigDataSerializer(serializers.Serializer):

    username_login_enabled = serializers.BooleanField(default=True, label=_('启用用户名登录'))
    username_register_enabled = serializers.BooleanField(
        default=True, label=_('启用用户名注册')
    )
    email_login_enabled = serializers.BooleanField(default=False, label=_('启用邮箱账号登录'))

    login_enabled_custom_field_names = serializers.ListField(
        child=serializers.CharField(), label=_('启用密码登录的自定义字段'), default=[]
    )
    register_enabled_custom_field_names = serializers.ListField(
        child=serializers.CharField(), label=_('启用密码注册的自定义字段'), default=[]
    )

    is_open_register_limit = serializers.BooleanField(default=False, label=('是否限制注册用户'))
    register_time_limit = serializers.IntegerField(default=1, label=_('用户注册时间限制(分钟)'))
    register_count_limit = serializers.IntegerField(default=10, label=_('用户注册数量限制'))

    is_open_authcode = serializers.BooleanField(default=False, label=_('是否打开验证码'))
    error_number_open_authcode = serializers.IntegerField(
        default=0, label=_('错误几次提示输入验证码')
    )


class PasswordLoginRegisterConfigSerializer(LoginRegisterConfigBaseSerializer):

    data = PasswordLoginRegisterConfigDataSerializer(label=_('配置数据'))


class PasswordLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class PasswordRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
