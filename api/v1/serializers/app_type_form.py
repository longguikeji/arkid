from rest_framework import serializers


class AppTypeFormSerializer(serializers.Serializer):

    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
