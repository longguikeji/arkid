"""
SAML2.0 SP注册序列器
"""
from common.provider import ExternalIdpProvider
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExternalIdpBaseSerializer
from api.v1.fields.custom import create_dowload_url_field, create_custom_dict_field, create_upload_file_field, create_upload_url_field


class Saml2SPExternalIdpSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    序列器
    """
    idp_xmldata_file = create_upload_file_field(serializers.CharField)(
        hint=_("请选择上传metadat文件"),
        label=_("元数据文件上传"),
        required=False
    )

    attribute_mapping = create_custom_dict_field(serializers.JSONField)(
        hint=_("清添加自定义属性"),
        required=False
    )

    img_url = create_upload_url_field(serializers.CharField)(
        hint=_("请上传图标"),
        required=False,
        label=_("图标")
    )

    login_url = serializers.CharField(
        read_only=True,
        label=_("登陆地址")
    )



class SAML2SPSerializer(ExternalIdpBaseSerializer):  # pylint: disable=abstract-method
    """
    APP序列器
    """

    data = Saml2SPExternalIdpSerializer(
        label=_('IDP配置')
    )

    # 因存在自动生成登陆链接故此处设置为非必须
    url = serializers.CharField(
        required=False
    )


class 
