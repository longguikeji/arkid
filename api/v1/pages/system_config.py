from openapi.utils import extend_schema_tags

tag = 'system_config'
path = tag
name = '系统配置'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/system/config',
            'method': 'get'
        },
        'item': {
            'update': {
                'read': {
                    'path': '/api/v1/system/config',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/system/config',
                    'method': 'put'
                }
            }
        }
    }
)