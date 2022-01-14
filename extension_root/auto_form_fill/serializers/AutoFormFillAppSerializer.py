from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer
from api.v1.fields.custom import create_hint_field, create_upload_url_field


class AutoFormFillConfigSerializer(serializers.Serializer):

    username_css = create_hint_field(serializers.CharField)(hint="请填写用户名的css selector")
    password_css = create_hint_field(serializers.CharField)(hint="请填写密码的css selector")
    submit_css = create_hint_field(serializers.CharField)(hint="请填写提交按钮的css selector")
    auto_login = serializers.BooleanField()


class AutoFormFillAppSerializer(AppBaseSerializer):
    logo = create_upload_url_field(serializers.URLField)(
        hint=_("请选择图标"), required=False
    )
    url = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    data = AutoFormFillConfigSerializer()
