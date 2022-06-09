from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer
from api.v1.fields.custom import create_dowload_url_field, create_custom_dict_field, create_upload_file_field


class SAML2IdpBaseConfigSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    序列器
    注意： 此处取名为IDP**意味着在arkid中IDP与SP是一对一匹配的(区别于单租户应用)
    """

    entity_id = serializers.CharField(
        required=True
    )

    acs = serializers.URLField(
        required=True
    )

    sls = serializers.URLField(
        required=True
    )

    cert = create_upload_file_field(serializers.FileField)(
        hint=_("请选择上传SP 加密公钥"),
        label=_("SP 加密公钥文件上传"),
        required=True
    )
    
    encrypt_saml_responses = serializers.BooleanField(
        required=False,
        default=False
    )
    
    sign_response = serializers.BooleanField(
        required=False,
        default=False
    )
    sign_assertion = serializers.BooleanField(
        required=False,
        default=False
    )
    
    idp_cert = create_dowload_url_field(serializers.CharField)(
        hint=_("点击下载"),
        label=_("IDP CERT"),
        read_only=True
    )
    
    idp_entity_id = serializers.CharField(
        label=_("IDP Entity ID"),
        required=False,
        read_only=True
    )

    idp_sso_url = serializers.CharField(
        label=_("IDP SSO Service URL"),
        required=False,
        read_only=True
    )

class SAML2IdpBaseSerializer(AppBaseSerializer):
    data = SAML2IdpBaseConfigSerializer(label=_('配置'))