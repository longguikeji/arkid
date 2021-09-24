from openapi.utils import extend_schema_tags

tag = 'subuser'
path = tag
name = '子账号管理'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/childaccounts/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'subuser.create',
                'description': '添加子账号',
                'icon': 'el-icon-plus',
            }
        },
        'local': {
            'switch': {
                'path': '/api/v1/childaccounts/{account_uuid}/check_type/',
                'method': 'get',
                'description': '切换为主账号',
                'icon': 'el-icon-switch-button'
            },
            'enter': {
                'path': '/api/v1/childaccounts/{account_uuid}/get_token/',
                'method': 'get',
                'description': '进入该账号',
                'icon': 'el-icon-position'
            },
            'delete': {
                'path': '/api/v1/childaccounts/{account_uuid}/detail/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

subuser_create_tag = 'subuser.create'
subuser_create_name = '添加子账号'

extend_schema_tags(
    subuser_create_tag,
    subuser_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/childaccounts/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/childaccounts/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)