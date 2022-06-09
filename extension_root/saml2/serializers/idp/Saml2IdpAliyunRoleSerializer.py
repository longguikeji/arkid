from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.v1.fields.custom import create_dowload_url_field, create_custom_dict_field, create_upload_file_field
from common.serializer import AppBaseSerializer

class Saml2IdpAliyunRoleConfigSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    序列器
    注意： 此处取名为IDP**意味着在arkid中IDP与SP是一对一匹配的(区别于单租户应用)
    """
    xmldata_file = create_upload_file_field(serializers.FileField)(
        hint=_("请选择上传metadat文件"),
        label=_("元数据文件上传"),
        required=False
    )
    
    role = serializers.CharField(
        label=_("Role"),
        required=True,
    )
    
    role_session_name = serializers.CharField(
        label=_("RoleSessionName"),
        required=False,
        default="username"
    )
    
    session_duration = serializers.CharField(
        label=_("SessionDuration"),
        required=False,
        default="1800"
    )
    
    idp_metadata = create_dowload_url_field(serializers.CharField)(
        hint=_("点击下载"),
        label=_("IDP元数据文件"),
        read_only=True
    )

class Saml2IdpAliyunRoleSerializer(AppBaseSerializer):
    """
    APP序列器
    """

    data = Saml2IdpAliyunRoleConfigSerializer(label=_('SP配置'))
    
    url = serializers.CharField(
        read_only=True
    )