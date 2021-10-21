from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import AuthorizationAgentBaseSerializer


class LDAPSyncAgentConfigSerializer(serializers.Serializer):

    server_uri = serializers.CharField()
    bind_dn = serializers.CharField()
    bind_password = serializers.CharField()
    user_base_dn = serializers.CharField(default="ou=user,dc=example,dc=org")
    group_base_dn = serializers.CharField(default="ou=group,dc=example,dc=org")
    user_object_class = serializers.CharField(default="inetOrgPerson")
    group_object_class = serializers.CharField(default="groupOfNames")
    user_attr_map = serializers.CharField(
        default='{"username": "cn", "first_name": "givenName", "last_name": "sn", "email": "mail"}')
    group_attr_map = serializers.CharField(default='{"name": "cn"}')
    use_tls = serializers.BooleanField(default=False)


class LDAPSyncAgentSerializer(AuthorizationAgentBaseSerializer):

    data = LDAPSyncAgentConfigSerializer(label=_('data'))
