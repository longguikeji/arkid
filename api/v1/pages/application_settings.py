from openapi.utils import extend_schema_tags

tag = 'application_settings'
path = 'application_settings'
name = '应用认证设置'


extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_settings/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'application_settings.create',
                'description': '添加应用认证设置',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'application_settings.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_settings/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

application_settings_create_tag = 'application_settings.create'
application_settings_create_name = '添加应用认证设置'

extend_schema_tags(
    application_settings_create_tag,
    application_settings_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_settings/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_settings/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

application_settings_update_tag = 'application_settings.update'
application_settings_update_name = '编辑应用认证设置'

extend_schema_tags(
    application_settings_update_tag,
    application_settings_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_settings/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_settings/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
