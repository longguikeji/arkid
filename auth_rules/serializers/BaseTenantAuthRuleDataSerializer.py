
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class BaseTenantAuthRuleDataSerializer(serializers.Serializer):

    app = serializers.ChoiceField(
        label=_("关联应用"),
        choices=(
            ("用户名密码", "短信验证码", "图形验证码", "邮箱验证码", "动态口令", "指纹", "人脸识别")
        )
    )

    major_auth_factor = serializers.ChoiceField(
        label=_("主要认证因素"),
        choices=(
            ("用户名密码", "短信验证码", "图形验证码", "邮箱验证码", "动态口令", "指纹", "人脸识别")
        )
    )

    times = serializers.IntegerField(
        label=_("失败次数"),
        default=1
    )

    second_auth_factor = serializers.ChoiceField(
        label=_("次要认证因素"),
        choices=(
            ("用户名密码", "短信验证码", "图形验证码", "邮箱验证码", "动态口令", "指纹", "人脸识别")
        )
    )
