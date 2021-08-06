from openapi.utils import extend_schema_tags

tag = 'webhook_history'
path = tag
name = 'Webhook历史记录'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/',
            'method': 'get'
        },
        'item': {
            'retrieve': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{parent_lookup_webhook}/history/{id}/',
                'method': 'get'
            }
        }
    }
)