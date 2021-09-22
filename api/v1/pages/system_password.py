from openapi.utils import extend_schema_tags

tag = 'system_password_manage'
path = 'system_password'
name = '密码管理'

system_password_manage_tag = 'system_password_manage'
system_password_manage_name = '系统平台密码复杂度管理'

extend_schema_tags(
    system_password_manage_tag,
    system_password_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/config/password_complexity/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'system_password_manage.create',
                'description': '添加系统密码规则'
            }
        },
        'local': {
            'update': {
                'tag': 'system_password_manage.update',
                'description': '编辑'
            },
            'delete': {
                'path': '/api/v1/config/password_complexity/{complexity_uuid}/',
                'method': 'delete',
                'description': '删除'
            }
        }
    }
)

system_password_manage_create_tag = 'system_password_manage.create'
system_password_manage_create_name = '创建平台密码新规则'

extend_schema_tags(
    system_password_manage_create_tag,
    system_password_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/config/password_complexity/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/config/password_complexity/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

system_password_manage_update_tag = 'system_password_manage.update'
system_password_manage_update_name = '编辑平台密码规则'

extend_schema_tags(
    system_password_manage_update_tag,
    system_password_manage_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/config/password_complexity/{complexity_uuid}/',
            'method': 'get',
        },
        'global': {
            'update': {
                'path': '/api/v1/config/password_complexity/{complexity_uuid}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)