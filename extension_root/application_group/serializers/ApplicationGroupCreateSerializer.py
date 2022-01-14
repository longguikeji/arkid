"""
ApplicationGroupCreateSerializer
"""
from api.v1.fields.custom import create_foreign_key_field
from app.models import App
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.serializer import DynamicFieldsModelSerializer
from ..models import ApplicationGroup
from api.v1.pages import app as app_page
from django.db.models import Q

class ApplicationGroupCreateSerializer(DynamicFieldsModelSerializer):
    
    apps = create_foreign_key_field(serializers.ListField)(
        model_cls=App,
        field_name='uuid',
        page=app_page.app_only_list_tag,
        child=serializers.CharField(),
        default=[],
        label=_('应用列表'),
        link = "apps",
        source="app_uuids"
    )
    
    class Meta:
        model = ApplicationGroup
        fields = [
            "uuid",
            "id",
            "name",
            "apps"
        ]

        extra_kwargs = {
            'uuid': {'read_only': True},
        }
        
    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name', '')
        apps = validated_data.get('app_uuids', None)
        
        group = ApplicationGroup(
            tenant = tenant,
            name = name,
        )
        group.save()
        if apps is not None:
            for app_uuid in apps:
                app = App.active_objects.get(uuid = app_uuid)
                for group in app.application_groups.all():
                    group.apps.remove(app)
                group.apps.add(app)
                
        group.save()
        
        return group
    
    def update(self, instance, validated_data):
        print("update",validated_data)
        instance.name = validated_data.get('name', '')
        apps = validated_data.get('app_uuids', None)
        instance.apps.clear()
        if apps is not None:
            for app_uuid in apps:
                print(app_uuid)
                app = App.active_objects.get(uuid = app_uuid)
                print(app)
                for group in app.application_groups.all():
                    group.apps.remove(app)
                
                instance.apps.add(app)
                
        instance.save()
        print(instance.apps)
        
        return instance

