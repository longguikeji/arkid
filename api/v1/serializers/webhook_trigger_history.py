from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from webhook.models import WebHookTriggerHistory


class WebHookTriggerHistorySerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = WebHookTriggerHistory

        fields = (
            'id',
            'uuid',
            'status',
            'request',
            'response',
        )
