from rest_framework import serializers
from oauth2_provider.models import Application
from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer

CLIENT_TYPE_CHOICES = [
    (Application.CLIENT_CONFIDENTIAL, _("Confidential")),
    (Application.CLIENT_PUBLIC, _("Public")),
]

GRANT_TYPE_CHOICES = [
    (Application.GRANT_AUTHORIZATION_CODE, _("Authorization code")),
    (Application.GRANT_IMPLICIT, _("Implicit")),
    (Application.GRANT_PASSWORD, _("Resource owner password-based")),
    (Application.GRANT_CLIENT_CREDENTIALS, _("Client credentials")),
    (Application.GRANT_OPENID_HYBRID, _("OpenID connect hybrid")),
]


class OAuth2ConfigSerializer(serializers.Serializer):

    redirect_uris = serializers.URLField()
    client_type = serializers.ChoiceField(choices=CLIENT_TYPE_CHOICES, default=Application.CLIENT_PUBLIC)
    grant_type = serializers.ChoiceField(choices=GRANT_TYPE_CHOICES, default=Application.GRANT_AUTHORIZATION_CODE)

    client_id = serializers.CharField(read_only=True)
    client_secret = serializers.CharField(read_only=True)
    authorize = serializers.URLField(read_only=True)
    token = serializers.URLField(read_only=True)


class OAuth2AppSerializer(AppBaseSerializer):

    # protocol_data = OAuth2ConfigSerializer()
    data = OAuth2ConfigSerializer(label='数据')


class OIDCConfigSerializer(serializers.Serializer):

    redirect_uris = serializers.URLField()
    client_type = serializers.ChoiceField(choices=CLIENT_TYPE_CHOICES, default=Application.CLIENT_PUBLIC)
    grant_type = serializers.ChoiceField(choices=GRANT_TYPE_CHOICES, default=Application.GRANT_AUTHORIZATION_CODE)

    client_id = serializers.CharField(read_only=True)
    client_secret = serializers.CharField(read_only=True)
    authorize = serializers.URLField(read_only=True)
    token = serializers.URLField(read_only=True)


class OIDCAppSerializer(AppBaseSerializer):

    # protocol_data = OIDCConfigSerializer()
    data = OAuth2ConfigSerializer()
