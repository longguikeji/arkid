from openapi.utils import extend_schema_tags

tag = 'sub_admin_config'
path = tag
name = '子管理员设置'

extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/childmanager/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'sub_admin_config.create',
                'description': '添加子管理员',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'sub_admin_config.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/childmanager/{childmanager_uuid}/detail/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

sub_admin_config_create_tag = 'sub_admin_config.create'
sub_admin_config_create_name = '添加子管理员'

extend_schema_tags(
    sub_admin_config_create_tag,
    sub_admin_config_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/childmanager/create',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/childmanager/create',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

sub_admin_config_update_tag = 'sub_admin_config.update'
sub_admin_config_update_name = '编辑子管理员'

extend_schema_tags(
    sub_admin_config_update_tag,
    sub_admin_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/childmanager/{childmanager_uuid}/detail/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/childmanager/{childmanager_uuid}/detail/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)