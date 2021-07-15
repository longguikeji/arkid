from openapi.utils import extend_schema_tags

tag = 'lr_config'
path = tag
name = '登录注册配置'

extend_schema_tags(
    tag,
    name,
    {
        'type':'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/config/',
            'method': 'get'
        },
        'page': {
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