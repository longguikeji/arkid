from openapi.utils import extend_schema_tags

tag = 'user_log'
path = tag
name = '用户行为日志'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user_log/',
            'method': 'get'
        }
    }
)