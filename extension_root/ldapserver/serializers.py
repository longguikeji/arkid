"""
ldap server注册序列器
"""
from os import read
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer


class PeopleConfigSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    序列器
    """
    uid = serializers.BooleanField(
        label=_("uid(唯一标识)"),
        default=True
    )

    cn = serializers.BooleanField(
        label=_("cn(用户名)"),
        default=True
    )

    givenName = serializers.BooleanField(
        label=_("givenName(姓氏)"),
        default=True
    )

    mail = serializers.BooleanField(
        label=_("mail(邮箱)"),
        default=False
    )

    telephoneNumber = serializers.BooleanField(
        label=_("telephoneNumber(电话号码)"),
        default=False
    )


class GroupConfigSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    序列器
    """
    id = serializers.BooleanField(
        label=_("id(唯一标识)"),
        default=True
    )

    cn = serializers.BooleanField(
        label=_("cn(群组名称)"),
        default=True
    )

class LdapServerConfigSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    序列器
    """

    people = PeopleConfigSerializer(
        label=_("用户信息设置")
    )

    group = GroupConfigSerializer(
        label=_("群组信息设置")
    )


class LdapServerSerializer(ExtensionBaseSerializer):  # pylint: disable=abstract-method
    """
    APP序列器
    """

    data = LdapServerConfigSerializer(label=_('Server 配置'))
