from openapi.utils import extend_schema_tags

tag = 'permission_list'
path = tag
name = '权限列表'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/permission/',
            'method': 'get'
        }
    }
)