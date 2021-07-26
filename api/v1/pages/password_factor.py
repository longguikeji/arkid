from openapi.utils import extend_schema_tags

tag = 'password_factor'
path = tag
name = '密码管理'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/',
            'method': 'get'
        },
        'page': {
            'create': {
                'tag': 'password_create'
            }
        },
        'item': {
            'update': {
                'tag': 'password_update'
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/{complexity_uuid}/detail/',
                'method': 'delete'
            }
        }
    }
)

password_create_tag = 'password_create'
password_create_name = '创建新密码规则'

extend_schema_tags(
    password_create_tag,
    password_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/',
            'method': 'post'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/',
                'method': 'post'
            }
        }
    }
)

password_update_tag = 'password_update'
password_update_name = '编辑密码规则'

extend_schema_tags(
    password_update_tag,
    password_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/{complexity_uuid}/detail/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/password_complexity/{complexity_uuid}/detail/',
                'method': 'patch'
            }
        }
    }
)