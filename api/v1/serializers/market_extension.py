
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class MarketPlaceExtensionSerializer(serializers.Serializer):

    name = serializers.CharField()
    description = serializers.CharField()
    version = serializers.CharField()
    homepage = serializers.CharField()
    logo = serializers.CharField()
    maintainer = serializers.CharField()
    tags = serializers.CharField()
    type = serializers.CharField()
    scope = serializers.CharField()
    uuid = serializers.UUIDField(default='')
    installed = serializers.ChoiceField(choices=(('已安装', '未安装')), default='未安装', label=_('是否安装'))
    enalbed = serializers.ChoiceField(choices=(('已启用', '未启用')), default='未启用', label=_('是否安装'))

    # class Meta:

    #     fields = (
    #         'id',
    #         'uuid',
    #         'name',
    #         'url',
    #         'description',
    #     )


class MarketPlaceExtensionTagsSerializer(serializers.Serializer):

    data = serializers.ListField(child=serializers.CharField(), label=_('标签'))
