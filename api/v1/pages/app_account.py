from openapi.utils import extend_schema_tags

tag = 'admin_app_account'
path = 'admin_app_account'
name = '表单代填账号'

admin_app_account_tag = 'admin_app_account'
admin_app_account_name = '表单代填应用账号管理'

extend_schema_tags(
    admin_app_account_tag,
    admin_app_account_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/admin_app_account/',
            'method': 'get',
        },
        'global': {
            'create': {
                'tag': 'admin_app_account.create',
                'description': '创建新应用内账号',
                'icon': 'el-icon-plus',
            }
        },
        'local': {
            'update': {
                'tag': 'admin_app_account.update',
                'description': '编辑',
                'icon': 'el-icon-edit',
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/admin_app_account/{account_uuid}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete',
            },
        },
    },
)

admin_app_account_create_tag = 'admin_app_account.create'
admin_app_account_create_name = '创建新应用内账号'

extend_schema_tags(
    admin_app_account_create_tag,
    admin_app_account_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/admin_app_account/',
            'method': 'post',
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/admin_app_account/',
                'method': 'post',
                'description': '确定',
            }
        },
    },
)

admin_app_account_update_tag = 'admin_app_account.update'
admin_app_account_update_name = '编辑应用内账号'

extend_schema_tags(
    admin_app_account_update_tag,
    admin_app_account_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/admin_app_account/{account_uuid}/',
            'method': 'get',
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/admin_app_account/{account_uuid}/',
                'method': 'put',
                'description': '确定',
            }
        },
    },
)
