"""
BaseArticleSerializer
"""
from common.provider import BaseAuthRuleProvider
from runtime import get_app_runtime
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from ..models import Article


class BaseArticleSerializer(BaseDynamicFieldModelSerializer):

    author_name = serializers.SerializerMethodField(
        label=_("作者")
    )

    reader_names = serializers.SerializerMethodField(
        label=_("阅看用户")
    )

    def get_author_name(self, obj):
        return obj.author.nickname or obj.author.username

    def get_reader_names(self, obj):
        reader_names = ",".join(
            [reader.nickname or reader.username for reader in obj.readers.all()])
        if reader_names == "":
            reader_names = _("暂无用户阅览")
        elif len(reader_names) > 50:
            reader_names = reader_names[:50] + "..."

        return reader_names

    class Meta:
        model = Article
        fields = [
            'uuid',
            "created",
            "title",
            "content",
            "author_name",
            "reader_names",
            "readed_times"
        ]

        extra_kwargs = {
            'uuid': {'read_only': True},
            'readed_times': {'read_only': True},
            'created': {'read_only': True},
        }
