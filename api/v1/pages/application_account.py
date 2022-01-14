from openapi.utils import extend_schema_tags

tag = 'application_account_manage'
path = 'application_account_manage'
name = '子系统账号绑定'

application_account_manage_tag = 'application_account_manage'
application_account_manage_name = '子系统账号绑定'

extend_schema_tags(
    application_account_manage_tag,
    application_account_manage_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'application_account_manage.create',
                'description': '绑定新子系统账号',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'application_account_manage.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account/{id}/',
                'method': 'delete',
                'description': '解绑',
                'icon': 'el-icon-delete'
            }
        }
    }
)

application_account_manage_create_tag = 'application_account_manage.create'
application_account_manage_create_name = '绑定新子系统账号'

extend_schema_tags(
    application_account_manage_create_tag,
    application_account_manage_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

application_account_manage_update_tag = 'application_account_manage.update'
application_account_manage_update_name = '更新子系统账号'

extend_schema_tags(
    application_account_manage_update_tag,
    application_account_manage_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_account/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
