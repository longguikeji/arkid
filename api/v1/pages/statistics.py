from openapi.utils import extend_schema_tags

tag = 'statistics'
path = tag
name = '统计图表'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'dashboard_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/statistics/',
            'method': 'get'
        }
    }
)