import json
from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from webhook.models import WebHook
from rest_framework import serializers
from common.event import Event


class WebHookSerializer(DynamicFieldsModelSerializer):
    available_events = serializers.SerializerMethodField()

    class Meta:
        model = WebHook

        fields = (
            'uuid',
            'name',
            'url',
            'content_type',
            'events',
            'available_events',
            'secret',
        )
        extra_kwargs = {
            'uuid': {'read_only': True},
            'content_type': {'read_only': True},
            'available_events': {'read_only': True},
        }

    def create(self, validated_data):
        tenant = self.context['tenant']
        name = validated_data.get('name')
        url = validated_data.get('url')
        secret = validated_data.get('secret')
        events = validated_data.get('events')
        events_json = json.loads(events)

        hook = WebHook.valid_objects.create(
            tenant=tenant, name=name, url=url, secret=secret, events=events_json
        )
        return hook

    def get_available_events(self, instance):
        from common.event import Event

        return Event.choices


class WebHookListResponseSerializer(WebHookSerializer):
    class Meta:
        model = WebHook
        fields = ('uuid', 'name', 'url', 'content_type', 'events')


class WebhookCreateRequestSerializer(WebHookSerializer):
    class Meta:
        model = WebHook
        fields = ('name', 'url', 'secret', 'events')
