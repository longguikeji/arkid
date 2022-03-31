from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer

from oauth2_provider.models import Application
from common.serializer import AppBaseSerializer
from api.v1.fields.custom import create_hint_field, create_upload_url_field


class ArkIDSaasIdpConfigSerializer(serializers.Serializer):
    
    client_id = serializers.CharField()
    client_secret = serializers.CharField()

    authorize_url = serializers.URLField()
    token_url = serializers.URLField()
    userinfo_url = serializers.URLField()
    img_url = serializers.URLField()


    login_url = serializers.URLField(read_only=True)
    callback_url = serializers.URLField(read_only=True)


class ArkIDSaasIdpSerializer(ExternalIdpBaseSerializer):

    data = ArkIDSaasIdpConfigSerializer(label=_('data'))


class OIDCPlatformConfigSerializer(serializers.Serializer):

    skip_authorization = serializers.BooleanField(default=False)
    redirect_uris = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    openapi_uris = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    version = serializers.CharField()
    client_type = serializers.ChoiceField(choices=Application.CLIENT_TYPES, default=Application.CLIENT_PUBLIC)
    grant_type = serializers.ChoiceField(choices=Application.GRANT_TYPES, default=Application.GRANT_AUTHORIZATION_CODE)
    algorithm = serializers.ChoiceField(choices=Application.ALGORITHM_TYPES, default=Application.NO_ALGORITHM)

    client_id = serializers.CharField(read_only=True)
    client_secret = serializers.CharField(read_only=True)
    authorize = serializers.URLField(read_only=True)
    token = serializers.URLField(read_only=True)
    userinfo = serializers.URLField(read_only=True)
    logout = serializers.URLField(read_only=True)


class OIDCAppPlatformSerializer(AppBaseSerializer):
    logo = create_upload_url_field(serializers.URLField)(
        hint=_("请选择图标"), required=False
    )
    url = create_hint_field(serializers.URLField)(hint="请填写正确的url格式")
    # protocol_data = OIDCConfigSerializer()
    data = OIDCPlatformConfigSerializer()
