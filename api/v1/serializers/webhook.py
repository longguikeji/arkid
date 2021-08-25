import json
from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from webhook.models import Webhook, WebhookEvent
from webhook.event_types import WebhookEventType
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
    events = serializers.MultipleChoiceField(choices=WebhookEventType.CHOICES)
    url = serializers.URLField()

    class Meta:
        model = Webhook

        fields = (
            'uuid',
            'name',
            'url',
            'events',
            'secret',
        )
        extra_kwargs = {
            'uuid': {'read_only': True},
        }

    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name')
        url = validated_data.get('url')
        secret = validated_data.get('secret')
        events = validated_data.pop('events', None)

        hook = Webhook.valid_objects.create(
            tenant=tenant, name=name, url=url, secret=secret
        )
        if events is not None:
            for event_type in events:
                WebhookEvent.valid_objects.create(event_type=event_type, webhook=hook)
        hook.save()
        return hook

    def update(self, instance, validated_data):
        events = validated_data.pop('events', None)
        if events is not None:
            instance.events.all().delete()
            for event_type in events:
                WebhookEvent.valid_objects.create(
                    event_type=event_type, webhook=instance
                )
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            'uuid': instance.uuid.hex,
            'name': instance.name,
            'url': instance.url,
            'secret': instance.secret,
            'events': [e.event_type for e in instance.events.all()]
        }

# class WebhookListResponseSerializer(WebhookSerializer):
#     class Meta:
#         model = Webhook
#         fields = ('uuid', 'name', 'url', 'events')


# class WebhookCreateRequestSerializer(WebhookSerializer):
#     class Meta:
#         model = Webhook
#         fields = ('name', 'url', 'secret', 'events')
