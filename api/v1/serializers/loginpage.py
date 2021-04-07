from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .tenant import TenantSerializer

class ButtonRedirectSerializer(serializers.Serializer):
    url = serializers.URLField(label=_('重定向地址'))
    params = serializers.JSONField(label=_('重定向参数'), required=False)

class ButtonHttpSerializer(serializers.Serializer):
    url = serializers.URLField(label=_('http请求地址'))
    method = serializers.CharField(label=_('http请求方法'))
    params = serializers.JSONField(label=_('http请求参数'), required=False)

class ButtonSerializer(serializers.Serializer):
    prepend = serializers.CharField(label=_('前置文字'), required=False)
    label = serializers.CharField(label=_('标签文字'), required=False)
    tooltip = serializers.CharField(label=_('提示文字'), required=False)
    long = serializers.BooleanField(label=_('是否为长按钮'), required=False)
    img = serializers.URLField(label=_('图片地址'), required=False)
    gopage = serializers.CharField(label=_('跳转的页面名字'), required=False)
    redirect = ButtonRedirectSerializer(label=_('重定向'), required=False)
    http = ButtonHttpSerializer(label=_('http请求'), required=False)
    delay = serializers.IntegerField(label=_('点击后延时（单位：秒）'), required=False)

LOGIN_FORM_ITEM_TYPES = [
    ('text','普通文本框'),
    ('password','密码')
]

class LoginFormItemSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=LOGIN_FORM_ITEM_TYPES, label=_('种类'))
    placeholder = serializers.CharField(label=_('文字提示'), required=False)
    name = serializers.CharField(label=_('名字'))
    append = ButtonSerializer(label=_('扩展按钮'), required=False)

class LoginFormSerializer(serializers.Serializer):
    label = serializers.CharField(label=_('表单名'))
    items = LoginFormItemSerializer(label=_('表单项'), many=True)
    submit = ButtonSerializer(label=_('表单提交'))

class LoginPageExtendSerializer(serializers.Serializer):
    title = serializers.CharField(label=_('页面扩展标题'))
    buttons = ButtonSerializer(many=True, label=_('扩展按钮'))

class LoginPageSerializer(serializers.Serializer):
    name = serializers.CharField(label=_('页面名字'))
    forms = LoginFormSerializer(label=_('表单'), many=True)
    bottoms = ButtonSerializer(label=_('表单下按钮'), many=True, required=False)
    extend = LoginPageExtendSerializer(label=_('扩展'), required=False)

class LoginPagesSerializer(serializers.Serializer):
    data = serializers.DictField(label=_('key：页面名字（name）'), child=LoginPageSerializer())
    tenant = TenantSerializer(label=_('租户'), allow_null=True)