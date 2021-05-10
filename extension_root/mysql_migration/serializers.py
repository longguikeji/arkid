from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer


class MysqlMigrationConfigSerializer(serializers.Serializer):

    host = serializers.CharField()
    port = serializers.CharField()
    user = serializers.CharField()
    passwd = serializers.CharField()
    db = serializers.CharField()


class MysqlMigrationSerializer(ExtensionBaseSerializer):

    data = MysqlMigrationConfigSerializer(label=_('data'))
