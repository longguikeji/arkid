from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import LoginRegisterConfigBaseSerializer
from api.v1.fields.custom import create_password_field


class EmailLoginRegisterConfigDataSerializer(serializers.Serializer):

    register_enabled = serializers.BooleanField(default=True, label=_('启用注册'))
    reset_password_enabled = serializers.BooleanField(
        default=True, label=_('启用通过邮件重置密码')
    )
    register_tmpl = serializers.CharField(label=_('注册邮件模板'), default='')
    reset_pwd_tmpl = serializers.CharField(label=_('重置密码邮件模板'), default='')
    auth_code_length = serializers.IntegerField(label=_('验证码位数'), default=6)
    # is_open_register_limit = serializers.BooleanField(default=False, label=('是否限制注册用户'))
    # register_time_limit = serializers.IntegerField(default=1, label=_('用户注册时间限制(分钟)'))
    # register_count_limit = serializers.IntegerField(default=10, label=_('用户注册数量限制'))


class EmailLoginRegisterConfigSerializer(LoginRegisterConfigBaseSerializer):

    data = EmailLoginRegisterConfigDataSerializer(label=_('配置数据'))


class EmailRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class EmailResetPasswordRequestSerializer(serializers.Serializer):

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
