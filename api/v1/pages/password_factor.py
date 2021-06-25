from openapi.utils import extend_schema_tags

tag = 'password_factor'
path = tag
name = '密码管理'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/',
            'method': 'get'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/',
                'method': 'post'
            }
        },
        'item': {
            'update': {
                'read': {
                    'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/{complexity_uuid}/detail/',
                    'method': 'get'
                },
                'write': {
                    'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/{complexity_uuid}/detail/',
                    'method': 'put'
                }
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/{complexity_uuid}/detail/',
                'method': 'delete'
            }   
        }
    }
)