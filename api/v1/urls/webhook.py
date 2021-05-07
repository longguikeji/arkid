from api.v1.views import (
    webhook as views_webhook,
    webhook_trigger_history as views_webhook_trigger_history,
)

from .tenant import tenant_router


tenant_webhook_router = tenant_router.register(r'webhook',
        views_webhook.WebHookViewSet,
        basename='tenant-webhook',
        parents_query_lookups=['tenant'])
        
tenant_webhook_router.register(r'history',
        views_webhook_trigger_history.WebHookTriggerHistoryViewSet,
        basename='tenant-webhook-history',
        parents_query_lookups=['tenant', 'webhook'])

