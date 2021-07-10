"""
SAML2.0 SP注册序列器
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import AppBaseSerializer
from api.v1.fields.custom import create_dowload_url_field


class SAMLasIDPConfigSerializer(serializers.Serializer): # pylint: disable=abstract-method
    """
    序列器
    注意： 此处取名为IDP**意味着在arkid中IDP与SP是一对一匹配的(区别于单租户应用)
    """

    entity_id = serializers.CharField(
        required=False
    )

    acs = serializers.URLField(
        required=False
    )

    sls = serializers.URLField(
        required=False
    )

    cert = serializers.CharField(
        label=_("证书公钥"),
        required=False
    )

    xmldata = serializers.CharField(
        label=_("元数据文件")
    )

    idp_metadata = create_dowload_url_field(serializers.CharField)(
        hint=_("点击下载"),
        label=_("IDP元数据文件"),
        read_only=True
    )

    sso_url = serializers.CharField(
        label=_("登陆地址"),
    )


class SAMLasIDPSerializer(AppBaseSerializer): # pylint: disable=abstract-method
    """
    APP序列器
    """

    data = SAMLasIDPConfigSerializer(label=_('SP配置'))

    # 因存在自动生成登陆链接故此处设置为非必须
    url = serializers.CharField(
        required=False
    )
