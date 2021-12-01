from openapi.utils import extend_schema_tags

tag = 'all_tenant'
path = tag
name = '租户列表'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/',
            'method': 'get'
        },
        'local': {
            'delete': {
                'path': '/api/v1/tenant/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)