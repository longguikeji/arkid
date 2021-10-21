from rest_framework import serializers


class AuthorizationServerSerializer(serializers.Serializer):

    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
