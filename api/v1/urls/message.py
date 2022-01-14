from extension_root.message.views import (
    MessageViewSet as view_message
)

from .tenant import tenant_router


tenant_message_router = tenant_router.register(
    r'message', view_message, basename='tenant-message', parents_query_lookups=['tenant'])
