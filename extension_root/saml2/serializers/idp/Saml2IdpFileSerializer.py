from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.v1.fields.custom import create_dowload_url_field, create_custom_dict_field, create_upload_file_field
from common.serializer import AppBaseSerializer

class Saml2IdpFileConfigSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    序列器
    注意： 此处取名为IDP**意味着在arkid中IDP与SP是一对一匹配的(区别于单租户应用)
    """
    xmldata_file = create_upload_file_field(serializers.FileField)(
        hint=_("请选择上传metadat文件"),
        label=_("元数据文件上传"),
        required=False
    )

    attribute_mapping = create_custom_dict_field(serializers.JSONField)(
        hint=_("请添加自定义属性"),
        label=_("自定义属性"),
        required=False
    )
    
    idp_metadata = create_dowload_url_field(serializers.CharField)(
        hint=_("点击下载"),
        label=_("IDP元数据文件"),
        read_only=True
    )

class Saml2IdpFileSerializer(AppBaseSerializer):
    """
    APP序列器
    """

    data = Saml2IdpFileConfigSerializer(label=_('SP配置'))