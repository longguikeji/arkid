from openapi.utils import extend_schema_tags

tag = 'webhook'
path = tag
name = 'Webhook'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'list': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/',
            'method': 'get'
        },
        'create': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/',
            'method': 'post'
        },
        'update': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
            'method': 'put'
        },
        'delete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/webhook/{id}/',
            'method': 'delete'
        }
    }
)