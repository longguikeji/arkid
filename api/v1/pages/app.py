from openapi.utils import extend_schema_tags

tag = 'app'
path = tag
name = '应用管理'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'list': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/',
            'method': 'get'
        },
        'create': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/',
            'method': 'post'
        },
        'update': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
            'method': 'put'
        },
        'delete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
            'method': 'delete'
        }
    }
)
