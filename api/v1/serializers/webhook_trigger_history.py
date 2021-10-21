from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from webhook.models import WebhookTriggerHistory


class WebhookTriggerHistorySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = WebhookTriggerHistory

        fields = (
            'id',
            'uuid',
            'status',
            'request',
            'response',
        )
