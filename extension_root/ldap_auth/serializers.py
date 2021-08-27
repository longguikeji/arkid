from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import AuthorizationAgentBaseSerializer


class LDAPAuthorizationAgentConfigSerializer(serializers.Serializer):

    server_uri = serializers.CharField()
    bind_dn = serializers.CharField()
    bind_password = serializers.CharField()
    user_base_dn = serializers.CharField(default="ou=user,dc=example,dc=org")
    user_object_class = serializers.CharField(default="inetOrgPersong")
    user_attr_map = serializers.CharField(
        default='{"username": "cn", "first_name": "givenName", "last_name": "sn", "email": "mail"}')
    use_tls = serializers.BooleanField(default=False)


class LDAPAuthorizationAgentSerializer(AuthorizationAgentBaseSerializer):

    data = LDAPAuthorizationAgentConfigSerializer(label=_('data'))
