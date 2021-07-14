from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer


class HuaWeiSMSConfigSerializer(serializers.Serializer):

    access_key = serializers.CharField(required=True, label=_('Access Key'))
    secret_key = serializers.CharField(required=True, label=_('Secret Key'))
    signature = serializers.CharField(required=True, label=_('Signature'))
    sender = serializers.CharField(required=True, label=_('Sender'))

    template_code = serializers.CharField(required=True, label='验证码通用文案模板ID')
    template_register = serializers.CharField(required=False, label='注册文案模板ID')
    template_reset_pwd = serializers.CharField(required=False, label='重置密码文案模板ID')
    template_activate = serializers.CharField(required=False, label='用户激活文案模板ID')
    template_reset_mobile = serializers.CharField(required=False, label='用户重置手机文案模板ID')
    template_login = serializers.CharField(required=False, label='登录文案模板ID')

    template_code_i18n = serializers.CharField(required=False, label='国际-验证码通用文案模板ID')
    template_register_i18n = serializers.CharField(required=False, label='国际-注册文案模板ID')
    template_reset_pwd_i18n = serializers.CharField(required=False, label='国际-重置密码文案模板ID')
    template_activate_i18n = serializers.CharField(required=False, label='国际-用户激活文案模板ID')
    template_reset_mobile_i18n = serializers.CharField(required=False, label='国际-用户重置手机文案模板ID')
    template_login_i18n = serializers.CharField(required=False, label='国际-登录文案模板ID')


class HuaWeiSMSSerializer(ExtensionBaseSerializer):
    data = HuaWeiSMSConfigSerializer(label=_('data'))
