from openapi.utils import extend_schema_tags

tag = 'application_group'
path = 'application_group'
name = '应用分组'


extend_schema_tags(
    tag,
    name,
    {
        'type': 'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_group/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'application_group.create',
                'description': '添加应用分组',
                'icon': 'el-icon-plus'
            }
        },
        'local': {
            'update': {
                'tag': 'application_group.update',
                'description': '编辑',
                'icon': 'el-icon-edit'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_group/{id}/',
                'method': 'delete',
                'description': '删除',
                'icon': 'el-icon-delete'
            }
        }
    }
)

application_group_create_tag = 'application_group.create'
application_group_create_name = '添加应用分组'

extend_schema_tags(
    application_group_create_tag,
    application_group_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_group/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_group/',
                'method': 'post',
                'description': '确定'
            }
        }
    }
)

application_group_update_tag = 'application_group.update'
application_group_update_name = '编辑应用分组'

extend_schema_tags(
    application_group_update_tag,
    application_group_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/application_group/{id}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/application_group/{id}/',
                'method': 'put',
                'description': '确定'
            }
        }
    }
)
