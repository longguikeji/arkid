import json
from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from webhook.models import Webhook, WebhookEvent
from rest_framework import serializers
from common.event import Event
from api.v1.fields.custom import (
    create_foreign_key_field,
    create_foreign_field,
    create_hint_field,
    create_mobile_field,
    create_password_field,
)

from ..pages import webhook


class WebhookEventSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = WebhookEvent

        fields = ('event_type',)
        extra_kwargs = {
            'event_type': {'read_only': True},
        }


class WebhookSerializer(DynamicFieldsModelSerializer):
    events = serializers.SerializerMethodField()
    set_events = create_foreign_key_field(serializers.ListField)(
        model_cls=WebhookEvent,
        field_name='event_type',
        page=webhook.tag,
        child=serializers.CharField(),
        write_only=True,
    )
    url = serializers.URLField()

    class Meta:
        model = Webhook

        fields = (
            'uuid',
            'name',
            'url',
            'events',
            'set_events',
            'secret',
        )
        extra_kwargs = {
            'uuid': {'read_only': True},
            'events': {'read_only': True},
        }

    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name')
        url = validated_data.get('url')
        secret = validated_data.get('secret')
        set_events = validated_data.pop('set_events', None)

        hook = Webhook.valid_objects.create(
            tenant=tenant, name=name, url=url, secret=secret
        )
        if set_events is not None:
            for event_type in set_events:
                WebhookEvent.valid_objects.create(event_type=event_type, webhook=hook)
        hook.save()
        return hook

    def update(self, instance, validated_data):
        set_events = validated_data.pop('set_events', None)
        if set_events is not None:
            instance.events.all().delete()
            for event_type in set_events:
                WebhookEvent.valid_objects.create(
                    event_type=event_type, webhook=instance
                )
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def get_events(self, instance):
        events = instance.events.all()
        ret = []
        for e in events:
            ret.append(e.event_type)
        return ret


# class WebhookListResponseSerializer(WebhookSerializer):
#     class Meta:
#         model = Webhook
#         fields = ('uuid', 'name', 'url', 'events')


# class WebhookCreateRequestSerializer(WebhookSerializer):
#     class Meta:
#         model = Webhook
#         fields = ('name', 'url', 'secret', 'events')
