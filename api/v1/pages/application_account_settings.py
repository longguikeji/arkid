from openapi.utils import extend_schema_tags

tag = 'application_account_settings_manage'
path = 'application_account_settings_manage'
name = '应用内账号设置'

application_account_settings_manage_tag = 'application_account_settings_manage'
application_account_settings_manage_name = '应用内账号设置管理'

extend_schema_tags(
    application_account_settings_manage_tag,
    application_account_settings_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account_settings/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'application_account_settings_manage.create',
                'description': '创建新应用内账号',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'application_account_settings_manage.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account_settings/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

application_account_settings_manage_create_tag = 'application_account_settings_manage.create'
application_account_settings_manage_create_name = '创建新应用内账号设置'

extend_schema_tags(
    application_account_settings_manage_create_tag,
    application_account_settings_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account_settings/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account_settings/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

application_account_settings_manage_update_tag = 'application_account_settings_manage.update'
application_account_settings_manage_update_name = '编辑应用内账号设置'

extend_schema_tags(
    application_account_settings_manage_update_tag,
    application_account_settings_manage_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account_settings/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account_settings/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
