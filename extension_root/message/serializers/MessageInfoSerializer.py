"""
BaseMessageSerializer
"""
from api.v1.fields.custom import create_foreign_key_field
from app.models import App
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import CustomUser
from ..models import Message
from api.v1.pages import app as app_page


class MessageInfoSerializer(BaseDynamicFieldModelSerializer):

    app_name = serializers.SerializerMethodField(
        label=_("应用名称")
    )

    def get_app_name(self, obj):
        return obj.app.name
    
    users = serializers.SerializerMethodField(
        label=_("接收用户")
    )
    
    type = serializers.SerializerMethodField(
        label=_("类型")
    )
    
    app_logo = serializers.SerializerMethodField(
        label=_("应用logo")
    )
    
    def get_app_logo(self,obj):
        return obj.app.logo
    
    def get_type(self,obj):
        type_dict = {
            "notice": _("通知"),
            "announcement": _("公告"),
            "ticket": _("工单")
        }
        return type_dict.get(obj.type,_("未知"))
    
    def get_users(self, obj):
        users_list = []
        for user in obj.users.all():
            custom_user = CustomUser.active_objects.filter(user=user).order_by('-id').first()
            users_list.append(custom_user.data.get('real_name',user.username) if custom_user else user.username)
        return ",".join(users_list)

    class Meta:
        model = Message
        fields = [
            "id",
            "title",
            "time",
            "content",
            "app_name",
            "uuid",
            "users",
            "url",
            "type",
            "app_logo",
        ]

        extra_kwargs = {
            'uuid': {'read_only': True},
            "app_name": {'read_only': True}
        }
