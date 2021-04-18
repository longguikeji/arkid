from openapi.utils import extend_schema_tags

tag = 'permission'
path = tag
name = '权限列表'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'list': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/permission/',
            'method': 'get'
        },
        'create': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/permission/',
            'method': 'post'
        },
        'update': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/permission/{id}/',
            'method': 'put'
        },
        'delete': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/permission/{id}/',
            'method': 'delete'
        }
    }
)