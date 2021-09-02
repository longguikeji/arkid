from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class TenantAuthRuleDataSerializer(serializers.Serializer):

    major_auth = serializers.MultipleChoiceField(
        label=_("主要认证因素"),
        choices=["用户名密码", "短信验证码", "图形验证码", "邮箱验证码", "动态口令", "指纹", "人脸识别"]
    )

    times = serializers.IntegerField(
        label=_("次数")
    )

    second_auth = serializers.MultipleChoiceField(
        label=_("主要认证因素"),
        choices=["用户名密码", "短信验证码", "图形验证码", "邮箱验证码", "动态口令", "指纹", "人脸识别"]
    )

    apps = serializers.MultipleChoiceField(
        label=_("应用"),
        choices=["小红书", "阿里云", "所有应用"]
    )
