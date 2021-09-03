from openapi.utils import extend_schema_tags

tag = 'password'
path = tag
name = '密码管理'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/config/password_complexity/?tenant={tenant_uuid}',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'password.create'
            }
        },
        'local': {
            'update': {
                'tag': 'password.update'
            },
            'delete': {
                'path': '/api/v1/config/password_complexity/{complexity_uuid}/?tenant={tenant_uuid}',
                'method': 'delete'
            }
        }
    }
)

password_create_tag = 'password.create'
password_create_name = '创建新密码规则'

extend_schema_tags(
    password_create_tag,
    password_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/config/password_complexity/?tenant={tenant_uuid}',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/config/password_complexity/?tenant={tenant_uuid}',
                'method': 'post'
            }
        }
    }
)

password_update_tag = 'password.update'
password_update_name = '编辑密码规则'

extend_schema_tags(
    password_update_tag,
    password_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/config/password_complexity/{complexity_uuid}/?tenant={tenant_uuid}',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/config/password_complexity/{complexity_uuid}/?tenant={tenant_uuid}',
                'method': 'patch'
            }
        }
    }
)