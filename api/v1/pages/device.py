from openapi.utils import extend_schema_tags

tag = 'device'
path = tag
name = '设备管理'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/device/',
            'method': 'get'
        },
        'filter': {
            'path': '/api/v1/device/',
            'method': 'get'
        },
        'global': {
            'export': {
                'path': '/api/v1/device_export/',
                'method': 'get'
            }
        },
        'local': {
            'delete': {
                'path': '/api/v1/device/{device_uuid}/detail/',
                'method': 'delete'
            }
        }
    }
)