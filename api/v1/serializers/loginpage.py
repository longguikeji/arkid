from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class ButtonRedirectSerializer(serializers.Serializer):
    url = serializers.URLField(label=_('重定向地址'))
    params = serializers.JSONField(label=_('重定向参数'))

class ButtonHttpSerializer(serializers.Serializer):
    url = serializers.URLField(label=_('http请求地址'))
    method = serializers.CharField(label=_('http请求方法'))
    params = serializers.JSONField(label=_('http请求参数'))

class ButtonSerializer(serializers.Serializer):
    prepend = serializers.CharField(label=_('前置文字'))
    label = serializers.CharField(label=_('标签文字'))
    tooltip = serializers.CharField(label=_('提示文字'))
    long = serializers.BooleanField(label=_('是否为长按钮'))
    img = serializers.URLField(label=_('图片地址'))
    gopage = serializers.CharField(label=_('跳转的页面名字'))
    redirect = ButtonRedirectSerializer(label=_('重定向'))
    http = ButtonHttpSerializer(label=_('http请求'))
    delay = serializers.IntegerField(label=_('点击后延时（单位：秒）'))

class LoginFormItemSerializer(serializers.Serializer):
    type = serializers.ChoiceField(label=_('种类'))
    placeholder = serializers.CharField(label=_('文字提示'))
    name = serializers.CharField(label=_('名字'))
    append = ButtonSerializer(label=_('扩展按钮'))

class LoginFormSerializer(serializers.Serializer):
    label = serializers.CharField(label=_('表单名'))
    items = LoginFormItemSerializer(label=_('表单项'), many=True)

class LoginPageExtendSerializer(serializers.Serializer):
    title = serializers.CharField(label=_('页面扩展标题'))
    buttons = ButtonSerializer(many=True, label=_('扩展按钮'))

class LoginPageSerializer(serializers.Serializer):
    forms = LoginFormSerializer(label=_('表单'), many=True)
    bottoms = ButtonSerializer(label=_('表单下按钮'), many=True)
    extend = LoginPageExtendSerializer(label=_('扩展'))

class LoginPagesSerializer(serializers.Serializer):
    login = LoginPageSerializer(label=_('登录页'))
    register = LoginPageSerializer(label=_('注册页'))

