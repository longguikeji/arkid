from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer

class ArkIDBindSerializer(serializers.Serializer):
    
    user_id = serializers.CharField()
    

class ArkIDExternalIdpConfigSerializer(serializers.Serializer):
    
    client_id = serializers.CharField()
    secret_id = serializers.CharField()

    authorize_url = serializers.URLField()
    token_url = serializers.URLField()
    userinfo_url = serializers.URLField()
    img_url = serializers.URLField()

    login_url = serializers.URLField(read_only=True)
    callback_url = serializers.URLField(read_only=True)
    bind_url = serializers.URLField(read_only=True)


class ArkIDExternalIdpSerializer(ExternalIdpBaseSerializer):

    data = ArkIDExternalIdpConfigSerializer(label=_('data'))
