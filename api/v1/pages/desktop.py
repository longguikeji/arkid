from openapi.utils import extend_schema_tags

tag = 'desktop'
path = tag
name = '桌面'

extend_schema_tags(
    tag,
    name,
    {
        'type':'dashboard_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{parent_lookup_user}/app/',
            'method': 'get'
        }
    }
)
