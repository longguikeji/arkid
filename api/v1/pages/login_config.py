from openapi.utils import extend_schema_tags

tag = 'login_config'
path = tag
name = '登录配置'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/config/',
            'method': 'get'
        },
        'item': {
            'update': {
                'write': {
                    'path': '/api/v1/tenant/{tenant_uuid}/config/',
                    'method': 'patch'
                },
                'read': {
                    'path': '/api/v1/tenant/{tenant_uuid}/config/',
                    'method': 'get'
                }
            }
        }
    }
)