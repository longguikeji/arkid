from openapi.utils import extend_schema_tags

tag = [
    'other_auth_factor_config',
]
path = 'other_auth'
name = '其他认证因素'

other_auth_factor_config_tag = 'other_auth_factor_config'
other_auth_factor_config_name = '其他认证因素插件化配置'

extend_schema_tags(
    other_auth_factor_config_tag,
    other_auth_factor_config_name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/other_auth_factor/?tenant={parent_lookup_tenant}',
            'method': 'get',
        },
        'global': {
            'create': {
                'tag': 'other_auth_factor_config.create',
                'description': '添加其他认证因素配置',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'other_auth_factor_config.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/other_auth_factor/{id}/?tenant={parent_lookup_tenant}',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            },
        },
    },
)

other_auth_factor_config_create_tag = 'other_auth_factor_config.create'
other_auth_factor_config_create_name = '添加其他认证因素配置'

extend_schema_tags(
    other_auth_factor_config_create_tag,
    other_auth_factor_config_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/other_auth_factor/?tenant={parent_lookup_tenant}',
            'method': 'post',
        },
        'global': {
            'create': {
                'path': '/api/v1/other_auth_factor/?tenant={parent_lookup_tenant}',
                'method': 'post',
                'description': '确定',
            }
        },
    },
)

other_auth_factor_config_update_tag = 'other_auth_factor_config.update'
other_auth_factor_config_update_name = '编辑其他认证因素配置'

extend_schema_tags(
    other_auth_factor_config_update_tag,
    other_auth_factor_config_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/other_auth_factor/{id}/?tenant={parent_lookup_tenant}',
            'method': 'get',
        },
        'global': {
            'update': {
                'path': '/api/v1/other_auth_factor/{id}/?tenant={parent_lookup_tenant}',
                'method': 'put',
                'description': '确定',
            }
        },
    },
)
