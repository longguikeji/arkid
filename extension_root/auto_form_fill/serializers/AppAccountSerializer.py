"""
ApplicationAccountSerializer
"""
from api.v1.fields.custom import create_foreign_key_field
from app.models import App
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import BaseDynamicFieldModelSerializer
from extension_root.auto_form_fill.models.AppAccount import AppAccount
from api.v1.pages import app as app_page


class AppAccountSerializer(BaseDynamicFieldModelSerializer):

    app_name = serializers.CharField(source="app.name", label=_("应用名称"))

    def get_app_name(self, obj):
        return obj.app.name

    app_uuid = create_foreign_key_field(serializers.CharField)(
        model_cls=App,
        field_name='uuid',
        page=app_page.app_only_list_tag,
        label=_('应用'),
        source="app.uuid",
    )

    class Meta:
        model = AppAccount
        fields = ["uuid", "app_name", "app_uuid", "username", "password"]

        extra_kwargs = {'uuid': {'read_only': True}, "app_name": {'read_only': True}}

    def create(self, validated_data):
        request = self.context['request']
        app_uuid = validated_data.get('app_uuid')
        username = validated_data.get('username')
        password = validated_data.get('password')

        app = App.valid_objects.filter(uuid=app_uuid).firt()
        app_account = AppAccount()
        app_account.app = app
        app_account.user = request.user
        app_account.username = username
        app_account.password = password
        app_account.save()
        return app_account

    def update(self, instance, validated_data):
        app_uuid = validated_data.get('app_uuid')
        username = validated_data.get('username')
        password = validated_data.get('password')

        app = App.valid_objects.filter(uuid=app_uuid).firt()
        instance.app = app
        instance.username = username
        instance.password = password
        instance.save()
        return instance
