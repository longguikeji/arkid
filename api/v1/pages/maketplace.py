from openapi.utils import extend_schema_tags

tag = 'maketplace'
path = tag
name = '插件市场'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'list': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/marketplace/',
            'method': 'get'
        },
        'create': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/marketplace/',
            'method': 'post'
        },
        'update': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/marketplace/{id}/',
            'method': 'put'
        },
        'delete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/marketplace/{id}/',
            'method': 'delete'
        }
    }
)