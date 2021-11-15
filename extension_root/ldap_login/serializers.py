from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import LoginRegisterConfigBaseSerializer


class LdapLoginConfigDataSerializer(serializers.Serializer):

    login_enabled = serializers.BooleanField(default=True, label=_('启用登录'))
    # register_enabled = serializers.BooleanField(default=False, label=_('启用注册'))

    host = serializers.CharField()
    port = serializers.IntegerField()
    bind_dn = serializers.CharField()
    bind_password = serializers.CharField()
    user_search_base = serializers.CharField(default="ou=user,dc=example,dc=org")
    user_object_class = serializers.CharField(default="inetOrgPerson")
    username_attr = serializers.CharField(default="cn")
    user_attr_map = serializers.CharField(
        default='{"username": "cn", "first_name": "givenName", "last_name": "sn", "email": "mail"}')
    use_tls = serializers.BooleanField(default=False)


class LdapLoginConfigSerializer(LoginRegisterConfigBaseSerializer):

    data = LdapLoginConfigDataSerializer(label=_('配置数据'))
