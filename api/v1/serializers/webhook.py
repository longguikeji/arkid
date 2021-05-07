from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from webhook.models import WebHook


class WebHookSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = WebHook

        fields = (
            'uuid',
            'name',
            'url',
            'content_type',
            'events',
        )
