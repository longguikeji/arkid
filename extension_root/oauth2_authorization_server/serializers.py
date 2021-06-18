from rest_framework import serializers
from oauth2_provider.models import Application
# from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer
from api.v1.fields.custom import create_hint_field


class OAuth2ConfigSerializer(serializers.Serializer):

    redirect_uris = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    client_type = serializers.ChoiceField(choices=Application.CLIENT_TYPES, default=Application.CLIENT_PUBLIC)
    grant_type = serializers.ChoiceField(choices=Application.GRANT_TYPES, default=Application.GRANT_AUTHORIZATION_CODE)

    client_id = serializers.CharField(read_only=True)
    client_secret = serializers.CharField(read_only=True)
    authorize = serializers.URLField(read_only=True)
    token = serializers.URLField(read_only=True)
    userinfo = serializers.URLField(read_only=True)


class OAuth2AppSerializer(AppBaseSerializer):
    url = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    # protocol_data = OAuth2ConfigSerializer()
    data = OAuth2ConfigSerializer(label='数据')


class OIDCConfigSerializer(serializers.Serializer):

    redirect_uris = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    client_type = serializers.ChoiceField(choices=Application.CLIENT_TYPES, default=Application.CLIENT_PUBLIC)
    grant_type = serializers.ChoiceField(choices=Application.GRANT_TYPES, default=Application.GRANT_AUTHORIZATION_CODE)
    algorithm = serializers.ChoiceField(choices=Application.ALGORITHM_TYPES, default=Application.NO_ALGORITHM)

    client_id = serializers.CharField(read_only=True)
    client_secret = serializers.CharField(read_only=True)
    authorize = serializers.URLField(read_only=True)
    token = serializers.URLField(read_only=True)
    userinfo = serializers.URLField(read_only=True)


class OIDCAppSerializer(AppBaseSerializer):

    # protocol_data = OIDCConfigSerializer()
    data = OIDCConfigSerializer()
